from scipy import stats

# GENERATION PARAMETERS
SEED = 150
N_users = 6000
N_years = 3
N_groups = 500
count_dist = stats.expon(scale=1.0)  # mean=1.0, var=1.0
N_posts = 10000
N_activities = 500
Avg_comments_per_post = 50
mode = "exponential" # user join date, options: "linear", "exponential"
rate = 0.6  # for exponential distribution of registration dates
START_YEAR = 2020


# USER PARAMETERS
GENERATED_NAMES_PATH = fr"generated_names"
COMANY_PATH = fr"companies.csv"

COUNTRIES = ["cz", "de", "pl", "nl"]


