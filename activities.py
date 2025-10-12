import numpy as np
from scipy.stats import truncnorm
import random as r
import pandas as pd

from parameters import *  # Parameters file

def generate_activities():
    np.random.seed(SEED)

    # --- parameters ---
    lower_dist, upper_dist = 3000, 15000
    mu_dist, sigma_dist = 5000, 2000
    a_dist = (lower_dist - mu_dist) / sigma_dist
    b_dist = (upper_dist - mu_dist) / sigma_dist

    lower_elev, upper_elev = 30, 200
    mu_elev, sigma_elev = 100, 50
    a_elev = (lower_elev - mu_elev) / sigma_elev
    b_elev = (upper_elev - mu_elev) / sigma_elev
        
    rng = np.random.default_rng(42)

    # --- distributions ---
    distances_m = truncnorm(a_dist, b_dist, loc=mu_dist, scale=sigma_dist).rvs(size=N_activities, random_state=rng)
    elev_per_km_m = truncnorm(a_elev, b_elev, loc=mu_elev, scale=sigma_elev).rvs(size=N_activities, random_state=rng)
    base_elev_m = rng.uniform(200, 400, size=N_activities)
    countries = rng.choice(['Czech Republic', 'Germany'], size=N_activities, p=[0.8, 0.2])
    total_elev_m = base_elev_m + distances_m * (elev_per_km_m / 1000.0)

    # --- country-specific regions ---
    regions_by_country = {
        "Czech Republic": [
            "Krkonoše Mountains",
            "Šumava National Park",
            "Bohemian Switzerland",
            "Jeseníky Mountains",
            "Beskydy Mountains"
        ],
        "Germany": [
            "Bavarian Alps",
            "Black Forest",
            "Harz Mountains",
            "Saxon Switzerland",
            "Thuringian Forest"
        ]
    }

    # --- assign regions efficiently ---
    # We can precompute masks
    mask_czech = countries == "Czech Republic"
    mask_germany = ~mask_czech

    # Create an empty array for regions
    regions = np.empty(N_activities, dtype=object)

    regions[mask_czech] = rng.choice(regions_by_country["Czech Republic"], size=mask_czech.sum())
    regions[mask_germany] = rng.choice(regions_by_country["Germany"], size=mask_germany.sum())

    # --- build dataframe ---
    df = pd.DataFrame({
        "country": countries,
        "region": regions,
        "distance_m": distances_m,
        "elev_per_km_m": elev_per_km_m,
        "base_elev_m": base_elev_m,
        "total_elev_m": total_elev_m,
    })

    # optional: round for readability
    df = df.round({'distance_m': 0, 'elev_per_km_m': 1, 'base_elev_m': 1, 'total_elev_m': 1})

    df['activity_id'] = np.arange(1, N_activities + 1)
    df = df[['activity_id', 'country', 'region', 'distance_m', 'elev_per_km_m', 'base_elev_m', 'total_elev_m']]

    df.to_csv('activities.csv', index=False)