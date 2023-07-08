from random import random
import numpy as np
import pandas as pd

gen_f = lambda f: 3.5 - 0.5 * np.log10(f) + 1 * (random() - 0.5)
thirds = [
    40,
    50,
    63,
    80,
    100,
    125,
    160,
    200,
    250,
    320,
    400,
    500,
    640,
    800,
    1000,
    1280,
    1600,
    2000,
    2500,
    3175,
    4000,
    5000,
    6300,
    8000,
]

columns = [
    *thirds,
    "microphone",
    "distance",
]

df = pd.DataFrame({f: [] for f in thirds})
for mic, distance in zip(range(28), range(3, 31)):
    reverberation_time = [gen_f(f) for f in thirds]
    row = pd.Series({f: rt for f, rt in zip(thirds, reverberation_time)})
    row["microphone"] = str(int(mic))
    row["distance"] = float(distance)
    row = row[columns]
    df = pd.concat([df, row.to_frame().T], ignore_index=True)

columns = [
    "microphone",
    "distance",
    *thirds,
]
df = df[columns]
df.to_csv("./data/mocked-measurement.csv", index=False)