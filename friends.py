import pandas as pd
import numpy as np
import time as t

from parameters import *

np.random.seed(SEED)

def generate_friends():
    print("---------- GENERATING FRIENDS MATRIX ----------")
    print("Reading users.csv...")
    udf = pd.read_csv('users.csv')

    print("Generating empty friend matrix...")
    actual_friend = np.zeros([len(udf), len(udf)]).astype(np.int8)

    country_map = udf['country'].to_numpy()[:, None] == udf['country'].to_numpy()[None, :]

    print(f"Creating initial population of 0.02 * N_users {int(0.02 * N_users)}/{N_users}...")
    initial_population = int(0.02 * N_users)

    for i in range(initial_population):
        for j in range(initial_population):
            if i == j:
                actual_friend[i, j] = 0
            if not actual_friend[i, j] == 1:
                if country_map[i, j]:
                    if np.random.rand() < 0.6:
                        actual_friend[i, j] = 1
                        actual_friend[j, i] = 1
                else:
                    if np.random.rand() < 0.1:
                        actual_friend[i, j] = 1
                        actual_friend[j, i] = 1

    print(f"Creating regular population of {int(N_users - initial_population)}/{N_users} users...")
    regular_population = int(N_users - initial_population)

    t1 = t.time()
    print(f"Populating matrix...")
    # i in [initial_population, N_users), j in [0, regular_population) with j < i
    rows = slice(initial_population, N_users)
    cols = slice(0, regular_population)

    # shapes
    n_i = N_users - initial_population
    n_j = regular_population

    # build the triangular mask j < i (with our row/col window)
    I = np.arange(n_i)[:, None]
    J = np.arange(n_j)[None, :]
    lower_tri_mask = (J < I)  # shape (n_i, n_j)

    # pull the window of the country map
    C = country_map[rows, cols]  # shape (n_i, n_j), dtype bool

    # probabilities per pair (0.05 if same country else 0.01)
    P = np.where(C, 0.05, 0.01)

    # draw randoms once and apply both the triangle and the prob test
    R = np.random.random(size=P.shape)
    edges = (R < P) & lower_tri_mask  # True where we create an edge

    # write to actual_friend (both directions), using indices to avoid view-assignment pitfalls
    ii, jj = np.where(edges)
    actual_friend[initial_population + ii, jj] = 1
    actual_friend[jj, initial_population + ii] = 1
    t2 = t.time()
    print(f"Took {(t2-t1)/60} minutes to generate friend matrix")

    print("Settings diagonal to 0...")
    np.fill_diagonal(actual_friend, 0)

    print("Saving to npy...")
    np.save('actual_friend.npy', actual_friend) # Takes ~1 GB
    # np.savetxt("friends.csv", actual_friend, delimiter=",") # Took 12+ GB
