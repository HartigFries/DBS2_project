# ------------------------- IMPORTS & SETUP -------------------------
from scipy import stats  # (kept if you import this elsewhere; not used directly below)
import numpy as np
import random as r
import pandas as pd
from datetime import datetime, date, time, timedelta
from scipy.stats import truncnorm
import string
from matplotlib import pyplot as plt  # not used here but left since you had it
import math
import calendar
from typing import Optional

from parameters import *

def generate_posts_tags_photos():
    print("---------- GENERATING POSTS / PHOTOS / TAGS ----------")
    print(f"Seeding RNGs with SEED={SEED}")
    r.seed(SEED)
    np.random.seed(SEED)

    # ------------------------- LOAD INPUTS -------------------------
    print("Reading users.csv...")
    udf = pd.read_csv('users.csv')
    print(f"Loaded {len(udf):,} users.")

    print("Loading friend matrix actual_friend.npy...")
    actual_friends = np.load("actual_friend.npy")
    print(f"Friend matrix shape: {actual_friends.shape}")

    print("Reading group_joins.csv...")
    gjdf = pd.read_csv("group_joins.csv")
    print(f"Loaded {len(gjdf):,} group join rows.")

    # Convenience
    n_users = len(udf)

    # Targets for user post volume distribution:
    # "Top p fraction of users has t share of posts"
    targets_user_posts = [(0.1, 0.8), (0.25, 0.92)]

    # ------------------------- POWER-LAW FIT HELPERS -------------------------
    def shares_from_params(a: float, c: int, n: int, ps):
        """
        Given parameters (a, c), population size n, and list ps=[(p, target_share), ...],
        compute the cumulative shares achieved by a Zipf-like weight model:
        weight(rank i) = 1 / (i + c)^a, ranks are 1..n (descending by activity).
        Returns only the shares (ignores the targets).
        """
        # weights descending by rank (i=1 is the "top")
        w = [1.0 / ((i + c) ** a) for i in range(1, n + 1)]
        S = sum(w)
        shares = []
        for p, _ in ps:
            k = max(1, int(round(p * n)))
            shares.append(sum(w[:k]) / S)
        return shares

    def fit_params(n: int, targets):
        """
        Coarse grid search over (a, c) to match desired (p -> share) targets.
        Returns (a, c).
        """
        best = None
        # Reasonable ranges: a in [0.5, 4.0], c in [0, 2n]
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

    # ------------------------- FIT USER→POST ALLOCATION -------------------------
    print("Fitting power-law parameters for user post counts...")
    a, c = fit_params(n_users, targets_user_posts)
    print(f"Fitted params for users: a={a:.3f}, c={c}")

    # Build descending weights for users (ranked 1..n_users)
    w = [1.0 / ((i + c) ** a) for i in range(1, n_users + 1)]

    # Allocate integer post counts per user summing exactly to N_posts (largest remainder)
    print(f"Allocating {N_posts:,} posts across {n_users:,} users...")
    total_w = sum(w)
    raw = [N_posts * wi / total_w for wi in w]
    x = [int(v) for v in raw]
    remainders = [(raw[i] - x[i], i) for i in range(n_users)]
    need = N_posts - sum(x)
    for _, i in sorted(remainders, reverse=True)[:need]:
        x[i] += 1

    # Shuffle user order so top-ranked users are not just first rows
    x = np.array(x, dtype=int)
    r.shuffle(x)
    print(f"Post count sanity: sum={x.sum()}, min={x.min()}, max={x.max()}")

    # ------------------------- DATE/TIME SAMPLING UTILITIES -------------------------
    # Try to import erfinv from scipy if math.erfinv not present
    try:
        from scipy.special import erfinv
    except ImportError:
        if hasattr(math, "erfinv"):
            erfinv = math.erfinv
        else:
            # Fallback polynomial approx for erfinv(x) in [-1,1]
            def erfinv(x: float) -> float:
                a_const = 0.147
                ln = math.log(1 - x * x)
                term1 = (2 / (math.pi * a_const)) + ln / 2
                term2 = ln / a_const
                return math.copysign(math.sqrt(math.sqrt(term1 * term1 - term2) - term1), x)

    def seconds_since_midnight(t: time) -> int:
        return t.hour * 3600 + t.minute * 60 + t.second

    def normal_cdf(x: float, mean: float, sd: float) -> float:
        """Standard normal CDF Φ((x-μ)/σ)."""
        z = (x - mean) / (sd * math.sqrt(2.0))
        return 0.5 * (1.0 + math.erf(z))

    def truncnorm_ppf(u: float, mean: float, sd: float, low: float, high: float) -> float:
        """Inverse-CDF sampler for truncated normal N(mean, sd^2) on [low, high)."""
        if not (high > low):
            raise ValueError("Empty interval in truncnorm_ppf")
        if sd <= 0:
            return float(np.clip(mean, low, np.nextafter(high, low)))

        a_ = normal_cdf(low, mean, sd)
        b_ = normal_cdf(high, mean, sd)
        if not (b_ > a_):
            return float(np.clip(mean, low, np.nextafter(high, low)))

        u01 = a_ + u * (b_ - a_)
        x_ = mean + sd * math.sqrt(2.0) * erfinv(2.0 * u01 - 1.0)
        return float(np.clip(x_, low, np.nextafter(high, low)))

    def days_in_month(y: int, m: int) -> int:
        return calendar.monthrange(y, m)[1]

    class DateSampler:
        """
        Fast date sampler between [min_dt, max_dt], weighting by:
        - geometric year decay
        - normal-like month preference
        - custom day-of-week weights
        """
        def __init__(
            self,
            min_dt: datetime,
            max_dt: datetime,
            *,
            year_decay: float = 0.95,
            month_mean: float = 7.0,
            month_sd: float = 2.0,
            dow_weights=(0.11, 0.10, 0.10, 0.11, 0.20, 0.23, 0.15),
        ):
            if max_dt < min_dt:
                raise ValueError("max_dt before min_dt")

            self.min_dt = min_dt
            self.max_dt = max_dt
            self.min_date = min_dt.date()
            self.max_date = max_dt.date()

            ndays = (self.max_date - self.min_date).days + 1
            self.dates = np.array(
                [self.min_date + timedelta(days=i) for i in range(ndays)],
                dtype="datetime64[D]"
            )

            # Year weights (geometric decay)
            years = np.array([int(str(d)[:4]) for d in self.dates], dtype=int)
            y0 = years.min()
            year_rel = years - y0
            year_w = (year_decay ** year_rel).astype(float)

            # Month weights (normal-like)
            months = np.array([int(str(d)[5:7]) for d in self.dates], dtype=int)
            if month_sd <= 0:
                peak = int(np.clip(int(round(month_mean)), 1, 12))
                month_w = (months == peak).astype(float)
                if month_w.sum() == 0:
                    month_w[:] = 1.0
            else:
                z = (months - month_mean) / month_sd
                month_w = np.exp(-0.5 * z * z)

            # Weekday weights
            dows = np.array(
                [(self.min_date + timedelta(days=i)).weekday() for i in range(ndays)],
                dtype=int
            )
            dow_w = np.array([dow_weights[w] for w in dows], dtype=float)

            w = year_w * month_w * dow_w
            if not np.isfinite(w).all() or w.sum() <= 0:
                w = np.ones_like(w, dtype=float)

            cdf = np.cumsum(w)
            cdf /= cdf[-1]
            self.cdf = cdf

        def sample_date(self, rng: np.random.Generator) -> date:
            u = rng.random()
            idx = np.searchsorted(self.cdf, u, side="right")
            if idx >= len(self.dates):
                idx = len(self.dates) - 1
            d64 = self.dates[idx]
            py_date = date.fromtimestamp(
                np.datetime64(d64, "s").astype("datetime64[s]").astype(int)
            )
            return py_date

    def generate_datetime_fast(
        min_dt: datetime,
        max_dt: datetime,
        *,
        year_decay: float = 0.95,
        month_mean: float = 7.0,
        month_sd: float = 2.0,
        dow_weights=(0.11, 0.10, 0.10, 0.11, 0.20, 0.23, 0.15),
        time_mean_hour: float = 18.0,
        time_sd_hours: float = 2.5,
        rng: Optional[np.random.Generator] = None,
        sampler: Optional[DateSampler] = None,
    ) -> datetime:
        """Sample a datetime constrained to [min_dt, max_dt] with realistic daily/seasonal patterns."""
        if rng is None:
            rng = np.random.default_rng()

        if sampler is None:
            sampler = DateSampler(
                min_dt,
                max_dt,
                year_decay=year_decay,
                month_mean=month_mean,
                month_sd=month_sd,
                dow_weights=dow_weights,
            )

        chosen_date = sampler.sample_date(rng)

        # Determine allowable seconds window for the chosen date
        low_secs = 0
        high_secs = 24 * 3600
        if chosen_date == sampler.min_date and chosen_date == sampler.max_date:
            low_secs = seconds_since_midnight(sampler.min_dt.time())
            high_secs = seconds_since_midnight(sampler.max_dt.time())
        elif chosen_date == sampler.min_date:
            low_secs = seconds_since_midnight(sampler.min_dt.time())
        elif chosen_date == sampler.max_date:
            high_secs = seconds_since_midnight(sampler.max_dt.time())

        if not (high_secs > low_secs):
            # Single moment — return exact datetime
            if sampler.min_dt == sampler.max_dt:
                return sampler.min_dt
            elif high_secs == low_secs:
                high_secs += 1
            else:
                low_secs, high_secs = high_secs, low_secs

        # Truncated normal time-of-day
        mean_secs = time_mean_hour * 3600.0
        sd_secs = max(1e-12, time_sd_hours * 3600.0)
        secs = truncnorm_ppf(rng.random(), mean_secs, sd_secs, low_secs, np.nextafter(high_secs, low_secs))
        secs = int(round(secs))

        dt = datetime.combine(chosen_date, time(0, 0, 0)) + timedelta(seconds=secs)
        if dt < sampler.min_dt:
            dt = sampler.min_dt
        elif dt > sampler.max_dt:
            dt = sampler.max_dt
        return dt

    # ------------------------- GENERATE POSTS (timestamps) -------------------------
    print("Generating per-post timestamps...")
    pdf_posts = {'user_id': [], 'post_id': [], 'created_at': []}

    rng = np.random.default_rng(SEED)
    max_date = udf['join_date'].astype('datetime64[s]').max() + timedelta(days=2)
    udf['join_date'] = udf['join_date'].astype('datetime64[s]')

    total_posts = int(x.sum())
    accum = 0
    for user_id in range(1, n_users + 1):
        if user_id % 1000 == 0 or user_id == 1 or user_id == n_users:
            print(f"  User {user_id:,}/{n_users:,} | posts for user: {x[user_id-1]} | progress: {accum:,}/{total_posts:,}")
        # Pre-build a sampler per user bounded by their join_date..max_date
        sampler = DateSampler(udf.loc[user_id - 1, 'join_date'], max_date, month_mean=7, month_sd=2)
        # Generate this user's timestamps
        samples = [generate_datetime_fast(udf.loc[user_id - 1, 'join_date'], max_date, rng=rng, sampler=sampler)
                for _ in range(x[user_id - 1])]

        # Append rows
        pdf_posts['user_id'].extend([user_id] * x[user_id - 1])
        pdf_posts['post_id'].extend(range(x[user_id - 1]))  # temporary per-user post_id; will reindex globally
        pdf_posts['created_at'].extend(samples)
        accum += x[user_id - 1]

    # Materialize and globally index posts
    jdf = pd.DataFrame(pdf_posts).sort_values(by=['created_at']).reset_index(drop=True)
    jdf['post_id'] = range(len(jdf))
    jdf['created_at'] = jdf['created_at'].astype('datetime64[s]')
    print(f"Generated {len(jdf):,} posts; time span: {jdf['created_at'].min()} → {jdf['created_at'].max()}")

    # ------------------------- (OPTIONAL) POWER-LAW FOR POST ATTENTION -------------------------
    # You re-fit a separate power-law for *posts* if needed (e.g., for likes/views sampling later).
    print("Fitting power-law parameters for post-level attention (optional downstream use)...")
    n_posts = len(jdf)
    targets_posts = [(0.1, 0.5), (0.75, 0.90)]
    a_p, c_p = fit_params(n_posts, targets_posts)
    print(f"Fitted params for posts: a={a_p:.3f}, c={c_p}")

    # Example: turn fitted post weights into integer 'attention credits' if you need them:
    w_posts = [1.0 / ((i + c_p) ** a_p) for i in range(1, n_posts + 1)]
    total_w_posts = sum(w_posts)
    raw_posts = [N_posts * wi / total_w_posts for wi in w_posts]
    credits = [int(v) for v in raw_posts]
    rema = [(raw_posts[i] - credits[i], i) for i in range(n_posts)]
    need = N_posts - sum(credits)
    for _, i in sorted(rema, reverse=True)[:need]:
        credits[i] += 1
    # (We don't use `credits` further below, but it mirrors your pattern.)

    # ------------------------- MAKE POSTS DATAFRAME (content + activity) -------------------------
    print("Building posts dataframe with text, activities, and photos...")
    df = pd.DataFrame()
    df['post_id'] = jdf['post_id'].unique()

    # Generate short random alnum strings per post
    df['text'] = [
        ''.join(r.choices(string.ascii_letters + string.digits,
                        k=r.choices(range(2, 30), k=1)[0]))
        for _ in range(len(jdf))
    ]

    # Exponential-decay weighting for activities (lower IDs more likely)
    scale = 500  # steeper decay -> smaller scale
    ax = np.arange(1, N_activities + 1)
    weights = np.exp(-ax / scale)
    weights /= weights.sum()

    # Choose activities for about half the posts
    activity_draws = r.choices(range(1, N_activities + 1), weights=weights, k=len(jdf)//2)
    activities = [np.nan] * (len(jdf) - len(activity_draws)) + activity_draws
    r.shuffle(activities)
    df['activity_id'] = activities

    # Randomly mask ~50% to NaN
    mask50 = np.random.rand(len(df)) < 0.5
    df.loc[mask50, 'activity_id'] = np.nan

    # ------------------------- PHOTO ATTACHMENTS -------------------------
    print("Assigning photos to some posts...")
    p_id = 1
    p_list = []
    for i in df['activity_id'].tolist():
        if np.isnan(i):
            # Less likely to get a photo if no activity
            if r.choices([True, False], weights=[0.3, 0.7])[0]:
                p_list.append(p_id); p_id += 1
            else:
                p_list.append(None)
        else:
            # More likely to get a photo if there is an activity
            if r.choices([True, False], weights=[0.6, 0.4])[0]:
                p_list.append(p_id); p_id += 1
            else:
                p_list.append(None)

    df['photo_id'] = pd.Series(p_list, dtype='Int64')
    df['activity_id'] = df['activity_id'].astype('Int64')

    N_photos = df['photo_id'].notna().sum()
    print(f"Total photos assigned: {N_photos:,}")

    # ------------------------- TAG SUGGESTIONS VIA FRIENDS/GROUPS -------------------------
    print("Preparing tag suggestions (friend/group influenced)...")

    # Non-commercial mask
    is_com = udf['is_commercial'].astype(bool)

    # Map: user_id -> np.array of group_ids the user belongs to
    user_groups_series = gjdf.groupby('user_id')['group_id'].apply(lambda x: np.array(x, dtype=int))

    # 1-based user IDs to include (non-commercial users)
    uids_1 = udf.loc[~is_com, 'user_id']

    # Ensure all non-commercial user_ids exist in the mapping (empty arrays if none)
    user_to_groups = user_groups_series.reindex(uids_1, fill_value=np.array([], dtype=int))

    # Group -> users mapping (1-based)
    groups_to_users = gjdf.groupby('group_id')['user_id'].apply(np.array)

    rng = np.random.default_rng(seed=SEED)

    # 0-based indices of non-commercial users
    uids0 = (uids_1.values - 1).astype(int)
    n_users_matrix = actual_friends.shape[1]

    # Base friend probability: 0.001 (i.e., 0.1%) per friend edge
    friend_prob = (actual_friends.astype(np.float16) * 0.001)

    # Pre-convert groups to 0-based arrays (for speed)
    groups_users0 = {int(gr): (np.asarray(users, dtype=np.int32) - 1)
                    for gr, users in groups_to_users.items()}

    user_samples = {}  # user_id (1-based) -> list of tagged user_ids (1-based)

    for idx, uid0 in enumerate(uids0, start=1):
        if idx % 2000 == 0 or idx == 1 or idx == len(uids0):
            print(f"  Tag sampling progress: {idx:,}/{len(uids0):,}")

        # Start from friend-driven probability vector (size n_users_matrix)
        p = friend_prob[uid0].copy()

        # Add small boost for users sharing any group with uid0 (+0.001 per shared group)
        for gr in user_to_groups.get(uid0 + 1, []):  # user_to_groups keyed by 1-based user_id
            if gr in groups_users0:
                idxs = groups_users0[gr]
                p[idxs] += 0.001

        # No self-tagging
        p[uid0] = 0.0

        # Clamp to [0,1] to be valid probabilities
        np.clip(p, 0.0, 1.0, out=p)

        # Independent Bernoulli draws for each candidate → set of tagged users (no duplicates)
        picks_mask = rng.random(n_users_matrix) < p
        sampled0 = np.flatnonzero(picks_mask)

        # Store as 1-based IDs
        user_samples[uid0 + 1] = (sampled0 + 1).tolist()

    # Map post author (from jdf['user_id']) to their suggested tags
    def random_subset_from_user(x):
        samples = user_samples.get(x, [])
        # Choose random subset size (can be zero)
        k = r.choice(range(len(samples) + 1))  # 0..len(samples)
        if k == 0:
            return []
        return rng.choice(samples, size=k, replace=False).tolist()
    jdf['tags'] = jdf['user_id'].apply(random_subset_from_user)
    tdf = jdf[['post_id', 'tags']]
    tdf.to_csv('tags.csv', index=False)


    counts = gjdf.groupby('group_id')['user_id'].count().to_numpy()
    def post_to_group(x):
        samples = user_to_groups.get(x, [])
        if len(samples) == 0:
            return []
        else:
            chances = [counts[gr - 1] for gr in samples]  # gr-1 for 0-based
            normalized_chances = np.array(chances) / sum(chances)
            if np.random.rand() < 0.7:
                return []
            else:
                return [rng.choice(samples, p=normalized_chances)]

    jdf['group_id'] = jdf['user_id'].apply(post_to_group)
    gpdf = jdf[['post_id', 'group_id']]
    gpdf = gpdf[gpdf['group_id'].apply(lambda x: len(x) > 0)]
    gpdf.to_csv('post_in_group.csv', index=False)

    # ------------------------- SYNTHETIC PHOTOS TABLE -------------------------
    print("Building photos table (synthetic bytes per photo)...")
    photos_df = pd.DataFrame({
        'photo_id': list(range(1, N_photos + 1)),
        'imgs': [np.random.randint(0, 256, size=768, dtype=np.uint8) for _ in range(N_photos)]
    })

    # ------------------------- SAVE OUTPUTS -------------------------
    print("Saving CSVs...")
    jdf.to_csv('user_shares_posts.csv', index=False)  # posts timeline: post_id, user_id, created_at
    df.to_csv('posts.csv', index=False)               # post content + activity + photo + tags
    photos_df.to_csv('photos.csv', index=False)       # synthetic photo bytes

    print("Done ✅")
