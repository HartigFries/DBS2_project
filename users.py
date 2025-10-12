import numpy as np
from os import path
import random as r
import pandas as pd
from datetime import date, timedelta
import numpy as np
from scipy.stats import truncnorm
import string

from parameters import *


def generate_users():
    r.seed(SEED)
    # Implied parameters
    N_reg = int(N_users * 0.85) # N_regular_users
    N_com = N_users - N_reg # N_commercial_user
    # -------------------------- HELPERS --------------------------
    def softmax_dist(dist, n, **rvs_kwargs):
        """
        dist: any *frozen* scipy.stats distribution (e.g., stats.norm(loc=0, scale=1))
        n: number of components
        """
        z = dist.rvs(size=n, **rvs_kwargs).astype(float)
        # softmax: positive and sums to 1
        z -= z.max()           # numerical stability
        w = np.exp(z)
        return sorted(w / w.sum(), reverse=True)


    def generate_random_string(min_length=8, max_length=16):
        # Define the character set: letters + digits + a few special characters
        characters = string.ascii_letters + string.digits + "!@#$%^&*_-"
        
        # Randomly choose the string length within the given range
        length = r.randint(min_length, max_length)
        
        # Generate the random string
        random_string = ''.join(r.choice(characters) for _ in range(length))
        return random_string

    def generate_email(name: str) -> str:
        """
        Generate an email address based on the given name.
        The email format is: <name>.<random_number>@example.com
        where <random_number> is a random integer between 100 and 999.
        """
        random_number = r.randint(100, 999)
        domain = r.choice(["example.com", "femail.com", "mail.com", "test.org", "demo.net"])
        email = f"{name.lower().replace(' ', '.')}.{random_number}@{domain}"
        return email

    def sample_dates_full_year(year, n, seed=None):
        """
        n dates in `year` from a Normal centered on July 31,
        truncated to [Jan 1, Dec 31]. Spread is auto-picked
        so samples come from throughout the year.
        """
        start = date(year, 1, 1)
        end   = date(year, 12, 31)
        n_days = (end - start).days + 1

        mu = (date(year, 7, 31) - start).days  # center at July 31
        # Pick sigma so the *farther* side is ~3σ away (≈99.7% inside year)
        sigma = max(mu, (n_days - 1) - mu) / 3.0

        a = (0 - mu) / sigma
        b = ((n_days - 1) - mu) / sigma

        rng = np.random.default_rng(seed)
        day_idx = truncnorm.rvs(a, b, loc=mu, scale=sigma, size=n, random_state=rng)
        day_idx = np.rint(day_idx).astype(int)
        return [start + timedelta(days=int(d)) for d in day_idx]



    # --------- USER GENERATION ---------
    print("---------- GENERATING USERS ----------")
    print(f"Generating {N_users} users ({N_reg} regular, {N_com} commercial) over {N_years} years...")
    print(f"Using {mode} distribution of user join dates.")

    print("Loading names...")
    country_dict = {}
    n = len(COUNTRIES)

    for iso in COUNTRIES:
        with open(path.join(GENERATED_NAMES_PATH,f"names_{iso}.txt"), "r", encoding="utf-8") as f:
            names = [line.strip() for line in f.readlines()]
        country_dict[iso] = names

    country_percentages = softmax_dist(count_dist, len(COUNTRIES), random_state=SEED)
    print("Country distribution:", {COUNTRIES[i]: f"{country_percentages[i]*100:.2f}%" for i in range(len(COUNTRIES))})

    usernames = []
    user_country = []

    print("Sampling regular user names...")
    for _ in range(N_reg):
        # Step 1: choose which list to sample from
        chosen_list_idx = r.choices(range(len(COUNTRIES)), weights=country_percentages, k=1)[0]
        
        # Step 2: choose a random element from that list
        chosen_list = country_dict[COUNTRIES[chosen_list_idx]]
        item = r.choice(chosen_list)
        
        usernames.append(item)
        user_country.append(COUNTRIES[chosen_list_idx])

    print("Sampling commercial user names...")
    with open("companies.csv", "r", encoding="utf-8") as f:
        com_brands = [line.strip() for line in f.readlines()][1:]

    com_brands = r.sample(com_brands, N_com)

    if mode == "linear":
        w = [i for i in range(1, N_years+1)]
    elif mode == "exponential":
        if rate is None:
            raise ValueError("Provide r>1 for exponential (or use mode='power' with alpha).")
        w = sorted([rate**(i-1) for i in range(1, N_years+1)])

    x = [int(N_users * wi / sum(w)) for wi in w]
    if sum(x) < N_users:
        x[-1] += (N_users - sum(x))

    print("Sampling user join dates...")
    dates = []
    for i in range(N_years):
        year = START_YEAR + i
        dates.extend(sample_dates_full_year(year, x[i], seed=SEED+i))

    df = pd.DataFrame()

    # Combine individual and commercial usernames into a single list
    df['username'] = usernames + com_brands

    # Mark each user as commercial (1) or not (0)
    df['is_commercial'] = [0] * N_reg + [1] * N_com

    # Generate synthetic email addresses from usernames
    df['email'] = df['username'].apply(generate_email)

    # Generate random passwords for all users
    df['password'] = [generate_random_string() for _ in range(N_users)]

    # Assign join dates
    df['join_date'] = dates

    # Assign countries (commercial users get random countries)
    df['country'] = user_country + [r.choice(COUNTRIES) for _ in range(N_com)]

    # Sort users chronologically by join date and reset index
    df = df.sort_values(by='join_date').reset_index(drop=True)

    # Add unique user IDs after sorting
    df['user_id'] = range(1, N_users + 1)

    # Reorder columns for clarity
    df = df[['user_id', 'username', 'is_commercial', 'email', 'password', 'join_date', 'country']]

    # -------------------------- OUTPUT --------------------------
    # Export the final synthetic user dataset to CSV
    df.to_csv("users.csv", index=False)