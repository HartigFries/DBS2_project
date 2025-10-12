# ------------------------- IMPORTS & SETUP -------------------------
import string
import numpy as np
import pandas as pd
from collections import defaultdict
from functools import lru_cache
import random as r

from parameters import *  # expects SEED, N_posts, etc.

def generate_comments():
    print("---------- GENERATING COMMENTS ----------")
    print(f"Seeding RNGs with SEED={SEED}")
    r.seed(SEED)
    np.random.seed(SEED)

    # ------------------------- LOAD INPUTS -------------------------
    print("Reading users.csv and user_shares_posts.csv...")
    udf = pd.read_csv('users.csv')
    pdf = pd.read_csv('user_shares_posts.csv')
    print(f"Loaded {len(udf):,} users and {len(pdf):,} posts.")

    print("Loading friend matrix actual_friend.npy...")
    actual_friends = np.load("actual_friend.npy")
    print(f"Friend matrix shape: {actual_friends.shape}")

    # Total comments to create (e.g., 50x posts)
    N_comments = N_posts * 50
    print(f"Planning to generate {N_comments:,} total comments.")

    # ------------------------- POWER-LAW HELPERS -------------------------
    def shares_from_params(a, c, n, ps):
        """
        Given parameters (a, c), population size n, and targets ps=[(p, target_share), ...],
        compute cumulative shares achieved by weights:
        weight(rank i) = 1 / (i + c)^a, for i in 1..n (descending by activity).
        Returns the shares (ignores the target values).
        """
        # weights descending by rank (i=1 is the "top")
        w = [1.0 / ((i + c) ** a) for i in range(1, n + 1)]
        S = sum(w)
        shares = []
        for p, _ in ps:
            k = max(1, int(round(p * n)))
            # share captured by the top-k items
            shares.append(sum(w[:k]) / S)
        return shares

    def fit_params(n, targets):
        """
        Coarse grid search over (a, c) to match desired (p -> share) targets.
        Returns (a, c). Fast enough for typical n.
        """
        best = None
        # reasonable ranges: a in [0.5, 4], c in [0, 2n]
        a_vals = [0.5 + i * 0.1 for i in range(0, 36)]       # 0.5..4.0
        c_vals = [int(i * (2*n) / 40) for i in range(0, 41)] # 0..2n in 41 steps
        for a in a_vals:
            for c in c_vals:
                shares = shares_from_params(a, c, n, targets)
                err = sum((shares[i] - targets[i][1])**2 for i in range(len(targets)))
                if best is None or err < best[0]:
                    best = (err, a, c, shares)
        err, a, c, shares = best
        return a, c

    # ------------------------- ALLOCATE COMMENTS PER USER -------------------------
    print("\nFitting power-law for per-user comment allocation...")
    n_users = len(udf)
    targets_user_comments = [(0.3, 0.8), (0.4, 0.92)]  # "Top p fraction has t share"
    a_u, c_u = fit_params(n_users, targets_user_comments)
    print(f"Fitted user-params: a={a_u:.3f}, c={c_u}")

    # Build descending weights for users (ranked 1..n_users)
    w_users = [1.0 / ((i + c_u) ** a_u) for i in range(1, n_users + 1)]

    # Allocate integer comment counts per user summing exactly to N_comments (largest remainder)
    print(f"Allocating {N_comments:,} comments across {n_users:,} users...")
    total_w_users = sum(w_users)
    raw_users = [N_comments * wi / total_w_users for wi in w_users]
    x_users = [int(v) for v in raw_users]
    rema_users = [(raw_users[i] - x_users[i], i) for i in range(n_users)]
    need_users = N_comments - sum(x_users)
    for _, i in sorted(rema_users, reverse=True)[:need_users]:
        x_users[i] += 1

    # Shuffle so the heaviest commenters aren't just first rows
    comments_per_user = np.array(x_users, dtype=int)
    r.shuffle(comments_per_user)
    print(f"User comments sanity: sum={comments_per_user.sum()}, "
        f"min={comments_per_user.min()}, max={comments_per_user.max()}")

    # ------------------------- POST-SIDE WEIGHTS (FOR PICKING WHICH POSTS GET COMMENTS) -------------------------
    print("\nFitting power-law for post selection weights (not integer counts; normalized weights)...")
    n_posts = len(pdf)
    targets_posts_weights = [(0.2, 0.8), (0.3, 0.92)]
    a_p, c_p = fit_params(n_posts, targets_posts_weights)
    print(f"Fitted post-params: a={a_p:.3f}, c={c_p}")

    # Build descending weights for posts (ranked 1..n_posts) and normalize → probabilities
    w_posts = [1.0 / ((i + c_p) ** a_p) for i in range(1, n_posts + 1)]
    total_w_posts = sum(w_posts)
    post_weight_probs = np.array([wi / total_w_posts for wi in w_posts], dtype=float)
    print(f"Post weight stats: sum≈{post_weight_probs.sum():.6f}, "
        f"min={post_weight_probs.min():.6e}, max={post_weight_probs.max():.6e}")

    # Example: draw a small diagnostic sample of post_ids to eyeball distribution
    diag_sample = r.choices(pdf['post_id'].tolist(), weights=post_weight_probs, k=10)
    print(f"Diagnostic post sample (10): {diag_sample}")

    # ------------------------- FRIEND LISTS PER POST AUTHOR -------------------------
    print("\nBuilding friend lists per post author...")
    # pdf['user_id'] expected to be 1-based and compatible with actual_friends indexing (0-based)
    pdf['friends'] = pdf['user_id'].apply(lambda x: np.where(actual_friends[x - 1] == 1)[0])
    print("Friend lists built (as numpy indices into users).")

    # ------------------------- PRECOMPUTE SAMPLING ARRAYS -------------------------
    print("\nPrecomputing arrays for fast sampling...")
    post_ids = pdf['post_id'].to_numpy()
    post_created = pd.to_datetime(pdf['created_at']).to_numpy()

    # Global weights / cumulative weights for weighted sampling over posts
    weights = post_weight_probs.astype(float)
    W_total = weights.sum()
    cumw_all = np.cumsum(weights) / W_total
    print(f"Global weight sum W_total={W_total:.6f} (should be ~1.0)")

    def _sample_from_cumw(cumw, k: int):
        """Sample k indices according to cumulative weights (inverse transform)."""
        u = np.random.random(k)
        return np.searchsorted(cumw, u)

    # Build inverted index: commenter (user_id-1) -> np.array(post_idx) where they are a friend of the author
    print("Building inverted index (friend_to_postidx)...")
    friend_to_postidx = defaultdict(list)
    for i, frs in enumerate(pdf['friends']):
        # frs: array of 0-based friend user indices of the author of post i
        for f in frs:
            friend_to_postidx[f].append(i)
    friend_to_postidx = {u: np.asarray(idxs, dtype=np.int32) for u, idxs in friend_to_postidx.items()}
    print(f"Inverted index entries: {len(friend_to_postidx):,} users with ≥1 friend-authored post.")

    # Cache restricted distributions to avoid recomputing per user
    @lru_cache(maxsize=10000)
    def _friend_subset_for_user(u: int):
        """
        For 1-based user_id u, return:
        - idx: np.array of post indices authored by u's friends
        - cumw_sub: cumulative weights over that subset
        - W_u: total weight mass in the subset
        If no friend posts, returns (None, None, 0.0).
        """
        idx = friend_to_postidx.get(u - 1)  # friend_to_postidx keyed by 0-based user index
        if idx is None or idx.size == 0:
            return None, None, 0.0
        w_sub = weights[idx]
        W_u = float(w_sub.sum())
        if W_u <= 0:
            return None, None, 0.0
        cumw_sub = np.cumsum(w_sub) / W_u
        return idx, cumw_sub, W_u

    # ------------------------- SAMPLER: POSTS & TIMES PER USER -------------------------
    lam = 0.3  # exponential lag rate (hours)
    bias_strength = 3.0  # amplifies probability of commenting on a friend’s posts
    print(f"\nSampling config: lam={lam}, bias_strength={bias_strength}")

    def sample_posts_and_times_for_user(user_id: int, n: int, lam: float = 0.3, bias_strength: float = 3.0):
        """
        Sample n (post_id, written_at) for a given 1-based user_id.
        Mixture: with probability p_friend,u pick from friend's posts; otherwise global.
        p_friend,u = clip(bias_strength * (friend-mass / global-mass), 0, 1)
        Times are post_created + Exp(lam) hours.
        """
        # Friend-restricted subset for this user (if any)
        idx_sub, cumw_sub, W_u = _friend_subset_for_user(user_id)

        # Compute friend-priority probability p_friend,u
        if W_u > 0:
            b_u = W_u / W_total
            p_friend = min(1.0, bias_strength * b_u)
        else:
            p_friend = 0.0

        # Number of this user's comments going to friends' posts
        m = np.random.binomial(n, p_friend)
        chosen_idx = np.empty(n, dtype=np.int32)

        # Sample m from friend subset
        if m > 0:
            sub_positions = _sample_from_cumw(cumw_sub, m)
            chosen_idx[:m] = idx_sub[sub_positions]

        # Sample remaining from global distribution
        if n - m > 0:
            global_positions = _sample_from_cumw(cumw_all, n - m)
            chosen_idx[m:] = global_positions

        # Map to post ids and base times
        chosen_post_ids = post_ids[chosen_idx]
        base_times = post_created[chosen_idx]

        # Exponential lag (in hours) from post creation to comment time
        offset_hours = np.random.exponential(scale=1 / lam, size=n)
        written_times = base_times + pd.to_timedelta(offset_hours, unit='h')

        return chosen_post_ids, written_times

    # ------------------------- GENERATION LOOP -------------------------
    print("\nGenerating comments...")
    records = []
    total_users = len(udf)
    total_comments_expected = int(comments_per_user.sum())
    accum_comments = 0

    for idx, (user_id, n_comments) in enumerate(zip(udf['user_id'], comments_per_user), start=1):
        if idx % 1000 == 0 or idx == 1 or idx == total_users:
            print(f"  User {idx:,}/{total_users:,} → user_id={user_id}, comments={n_comments} | "
                f"progress: {accum_comments:,}/{total_comments_expected:,}")

        if n_comments <= 0:
            continue

        chosen_posts, written_times = sample_posts_and_times_for_user(
            user_id, int(n_comments), lam=lam, bias_strength=bias_strength
        )

        # Random short alnum comment contents
        contents = [
            ''.join(r.choices(string.ascii_letters + string.digits + ' ', k=r.randint(1, 20)))
            for _ in range(int(n_comments))
        ]

        records.append(pd.DataFrame({
            'user_id': user_id,
            'post_id': chosen_posts,
            'written_at': written_times,
            'content': contents
        }))

        accum_comments += int(n_comments)

    # ------------------------- MATERIALIZE & SAVE -------------------------
    print("\nConcatenating records...")
    df = pd.concat(records, ignore_index=True) if records else pd.DataFrame(
        columns=['user_id', 'post_id', 'written_at', 'content']
    )
    df['written_at'] = df['written_at'].astype('datetime64[s]')

    print(f"Generated {len(df):,} comments.")
    if len(df) > 0:
        print(f"Time span: {df['written_at'].min()} → {df['written_at'].max()}")
        # Simple sanity checks
        uniq_users = df['user_id'].nunique()
        uniq_posts = df['post_id'].nunique()
        print(f"Unique commenting users: {uniq_users:,} | Unique commented posts: {uniq_posts:,}")

    print("Saving to comments.csv...")
    df.to_csv('comments.csv', index=False)
    print("Done ✅")
