import pandas as pd
from datetime import date, timedelta
from scipy.sparse import csr_matrix
import numpy as np
import random as r
import time as t

from parameters import *

def generate_groups():
    # ------------------------- SETUP -------------------------
    print("---------- GENERATING GROUPS + JOINS ----------")
    print(f"Seeding RNGs with SEED={SEED}")
    r.seed(SEED)
    np.random.seed(SEED)

    # ------------------------- HELPERS -------------------------
    def sample_date_around_date(start: date, n: int = 90, seed: int = 150) -> date:
        """
        Sample a date in [start + n, start + 2n] days (uniformly).
        If n == 0 -> returns start. If n < 0 -> raises.
        """
        if n < 0:
            raise ValueError("n must be non-negative")
        if n == 0:
            return start

        rng = np.random.default_rng(seed)
        # rng.integers(low, high) has exclusive 'high', so 2*n+1 makes 2*n inclusive.
        day_idx = rng.integers(n, 2 * n + 1)
        return start + timedelta(days=int(day_idx))

    # ------------------------- LOAD USERS -------------------------
    print("Reading users.csv...")
    udf = pd.read_csv('users.csv')
    print(f"Loaded {len(udf):,} users total.")

    print("Filtering out commercial users...")
    udf = udf[~udf['is_commercial'].astype(bool)]
    print(f"Kept {len(udf):,} non-commercial users.")

    print("Parsing join_date to datetime...")
    udf['join_date'] = pd.to_datetime(udf['join_date'])

    # ------------------------- INIT GROUP DF -------------------------
    print(f"Preparing {N_groups:,} groups...")
    df = pd.DataFrame()

    # Draw group countries proportional to user country distribution
    country_weights = udf['country'].value_counts(normalize=True).to_numpy()
    COUNTRY_CHOICES_PREVIEW = ", ".join(map(str, udf['country'].value_counts().index[:5]))
    print(f"Country weights computed (top samples: {COUNTRY_CHOICES_PREVIEW} ...).")

    df['group_country'] = r.choices(COUNTRIES, weights=country_weights, k=N_groups)
    df['group_name'] = [f'Group {i}' for i in range(1, N_groups + 1)]
    df['group_id'] = range(1, N_groups + 1)

    # ------------------------- USER JOIN CHANCES -------------------------
    default_active_joiners_chance = 2 / N_groups
    default_join_chance = 0.5 / N_groups
    low_join_chance = 0.25 / N_groups

    print("Assigning per-user baseline join chances...")
    udf['join_chance'] = r.choices(
        [default_active_joiners_chance, default_join_chance, low_join_chance],
        weights=[0.5, 0.3, 0.2],
        k=len(udf)
    )

    # ------------------------- GROUP CATEGORIES + BOOSTS -------------------------
    print("Shuffling group indices and splitting into popularity categories...")
    all_indices = np.arange(N_groups)
    np.random.shuffle(all_indices)

    split_sizes = [int(0.25 * N_groups), int(0.20 * N_groups), int(0.30 * N_groups), int(0.25 * N_groups)]
    split_sizes[-1] = N_groups - sum(split_sizes[:-1])  # absorb remainder into last split
    popular_idx, big_idx, small_idx, dead_idx = np.split(all_indices, np.cumsum(split_sizes)[:-1])

    df['category'] = 'unknown'
    df.loc[popular_idx, 'category'] = 'popular'
    df.loc[big_idx, 'category'] = 'big'
    df.loc[small_idx, 'category'] = 'small'
    df.loc[dead_idx, 'category'] = 'mostly_dead'

    boost_map = {'popular': 8, 'big': 4, 'small': 2, 'mostly_dead': 0.2}
    df['boost'] = df['category'].map(boost_map).to_numpy()

    print("Category counts:")
    print(df['category'].value_counts())

    # ------------------------- LOAD FRIEND GRAPH -------------------------
    print("Loading actual_friend.npy (symmetric 0/1 matrix)...")
    actual_friend = np.load('actual_friend.npy', allow_pickle=True).astype(np.int8)
    print(f"Friend matrix shape: {actual_friend.shape}")

    # ------------------------- PRECOMPUTED VECTORS -------------------------
    df_temp = df.copy()
    gr_country_array = np.array(df_temp['group_country'].to_list())
    gr_id = np.array(df_temp['group_id'].to_list(), dtype=np.int64)
    G = len(gr_id)
    N = actual_friend.shape[0]  # number of users in friend matrix

    # Placeholder (unused)
    gr = np.zeros(len(df_temp), dtype=int)

    rng = np.random.default_rng(SEED)
    max_date = udf['join_date'].max() + timedelta(days=2)

    # For quick membership appends per group
    member_dict = {int(gid): [] for gid in df['group_id']}

    # Accumulate joins here; convert to DataFrame at the end
    jdf_dict = {'group_id': [], 'user_id': [], 'join_date': []}

    # ------------------------- SPARSE MEMBERSHIP SETUP -------------------------
    print("Building initial (empty) sparse membership matrix M (users x groups)...")
    group_id_to_col = {int(g): i for i, g in enumerate(gr_id)}

    # Empty because member_dict is empty at this stage
    rows, cols = [], []
    data = np.ones(len(rows), dtype=np.int8)
    M = csr_matrix((data, (rows, cols)), shape=(N, G))
    print("NOTE: M is built once and NOT updated during the user loop; friend boosts will be 1.0 unless you rebuild/update M.")

    # ------------------------- MAIN USER LOOP -------------------------
    print("Sampling user joins across groups...")
    t_start = t.time()
    for idx, user in enumerate(udf.itertuples(index=False), start=1):
        # Progress ticker every ~1k users
        if idx % 1000 == 0 or idx == 1 or idx == len(udf):
            print(f"  Processing user {idx:,}/{len(udf):,} (user_id={user.user_id})")

        # Base chance with country match boost (3x if same country)
        chance_list = np.where(
            gr_country_array == user.country,
            float(user.join_chance) * 3.0,
            float(user.join_chance)
        ).astype(float)

        # Friend vector for this user (0/1 for friendship with every user)
        # NOTE: relies on positional alignment between udf rows and actual_friend rows
        friends_vec = actual_friend[idx - 1]  # idx-1 because enumerate started at 1

        # Friends in each group via sparse product (but M is empty/constant here -> zeros)
        friends_in_group = friends_vec @ M
        if not isinstance(friends_in_group, np.ndarray):
            friends_in_group = friends_in_group.A.ravel()
        else:
            friends_in_group = friends_in_group.ravel()

        # Friend-based boost: +0.5 per friend in group, capped at 3x; no friends => 1x
        boosts = 1 + 0.5 * friends_in_group
        np.minimum(boosts, 3, out=boosts)
        boosts[friends_in_group == 0] = 1.0

        # Apply boosts and group-category boost
        chance_list *= boosts
        chance_list *= df['boost'].to_numpy()

        # Bernoulli draws per group to decide joins for this user
        true_list = np.random.rand(len(chance_list)) < chance_list
        chosen_groups = gr_id[true_list]
        k = len(chosen_groups)

        if k:
            # Random offsets up to 180 days, clipped by max_date
            offsets = rng.integers(0, 180, size=k)
            join_dates = np.minimum(
                user.join_date + np.array([timedelta(days=int(d)) for d in offsets]),
                max_date
            )

            jdf_dict['group_id'].extend(chosen_groups.tolist())
            jdf_dict['user_id'].extend([user.user_id] * k)
            jdf_dict['join_date'].extend(join_dates.tolist())

            # Track membership (0-based index for friends matrix)
            for g in chosen_groups:
                member_dict[int(g)].append(int(user.user_id - 1))

    t_end = t.time()
    print(f"Finished sampling joins in {t_end - t_start:.2f}s.")

    # ------------------------- ENSURE NO EMPTY GROUPS -------------------------
    print("Ensuring each group has at least one member...")
    existing_groups_with_joins = set(jdf_dict['group_id'])
    empty_groups = [g for g in range(1, N_groups + 1) if g not in existing_groups_with_joins]
    print(f"Empty groups found: {len(empty_groups)}")

    for group in empty_groups:
        # Choose a random user and a plausible early join date
        chosen_user_id = r.choice(udf['user_id'].to_list())
        join_date = sample_date_around_date(udf['join_date'].min(), n=180, seed=SEED)

        jdf_dict['group_id'].append(group)
        jdf_dict['user_id'].append(chosen_user_id)
        jdf_dict['join_date'].append(join_date)

        # ✅ FIX: append the same chosen user (0-based) to member_dict (was previously using a stale 'user')
        member_dict[group].append(int(chosen_user_id - 1))

    # ------------------------- BUILD JOINS DF -------------------------
    print("Materializing joins DataFrame...")
    jdf = pd.DataFrame(jdf_dict)
    print(f"Total join rows: {len(jdf):,}")

    # ------------------------- CREATOR SELECTION -------------------------
    print("Selecting earliest join per group to determine group creator and creation date...")

    # 1) earliest join row index per group
    idx_earliest = jdf.groupby('group_id')['join_date'].idxmin()
    gmin = (
        jdf.loc[idx_earliest, ['group_id', 'join_date']]
        .rename(columns={'join_date': 'group_min_date'})
        .reset_index()  # keep original row index to write back later
    )

    # 2) for each group's earliest join, replace with a user who joined the platform
    #    on/before that date, picking the closest earlier one
    udf_small = udf[['user_id', 'join_date']].sort_values('join_date')
    gmin_sorted = gmin.sort_values('group_min_date')

    repl = pd.merge_asof(
        gmin_sorted,
        udf_small,
        left_on='group_min_date',
        right_on='join_date',
        direction='backward'
    )

    # Some groups may not have an earlier user; drop those
    repl = repl.dropna(subset=['user_id']).rename(
        columns={'join_date': 'new_join_date', 'user_id': 'new_user_id'}
    )

    # 3) write back (replace earliest join with found user/date)
    jdf.loc[repl['index'], 'user_id'] = repl['new_user_id'].to_numpy()
    jdf.loc[repl['index'], 'join_date'] = repl['new_join_date'].to_numpy()

    # ------------------------- EXTRACT CREATOR + CREATION DATE -------------------------
    print("Deriving group creators and creation dates...")
    first_joins = (
        jdf.sort_values(['group_id', 'join_date'])
        .drop_duplicates('group_id', keep='first')
        .set_index('group_id')
    )

    df['creator_id'] = first_joins.loc[df['group_id'], 'user_id'].to_numpy()
    df['creation_date'] = first_joins.loc[df['group_id'], 'join_date'].to_numpy()
    df = df[['group_id', 'group_name', 'group_country', 'creator_id', 'creation_date']]

    # ------------------------- SAVE OUTPUTS -------------------------
    print("Saving group_joins.csv...")
    jdf.to_csv('group_joins.csv', index=False)

    print("Saving groups.csv...")
    df = df.sort_values('group_id')
    df.to_csv('groups.csv', index=False)

    print("Done ✅")
