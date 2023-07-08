from random import random

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
from plotly import graph_objects as go

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
# df = pd.DataFrame({f: rt for f, rt in zip(thirds, reverberation_time)},)
df = pd.DataFrame({f: [] for f in thirds})

for i in range(3, 31):
    reverberation_time = [gen_f(f) for f in thirds]
    row = pd.Series({f: rt for f, rt in zip(thirds, reverberation_time)})
    row["distance"] = i
    df = pd.concat([df, row.to_frame().T], ignore_index=True)

# print(df.head())

# Plotly
# print(df)
# px.line(data_frame=df, x="")

# fig = px.scatter(df, x=df.columns, y=df.index)
# fig.show()

parameter = "RT [s]"
rails_top = []
rails_bottom = []
means = []
for freq in thirds:
    rails_top.append(df[freq].mean() + 1 * df[freq].std())
    rails_bottom.append(df[freq].mean() - 1 * df[freq].std())
    means.append(df[freq].mean())

fig = go.Figure()  # .update_layout(template="plotly_dark")
# for _, rt in df.iterrows():
# fig.add_trace(go.Scatter(x=thirds, y=rt, mode="markers"))
fig.add_trace(
    go.Scatter(
        name="Mean", x=thirds, y=means, mode="lines", marker=dict(color="#000"), line=dict(width=3)
    )
)
fig.update_xaxes(title="Frequency [Hz]", type="log")

fig.add_trace(
    go.Scatter(
        name="Mean + 1 StD",
        x=thirds,
        y=rails_top,
        mode="lines",
        marker=dict(color="#000"),
        line=dict(width=0),
        showlegend=False,
    )
)

fig.add_trace(
    go.Scatter(
        name="Mean - 1 StD",
        x=thirds,
        y=rails_bottom,
        mode="none",
        marker=dict(color="#000"),
        line=dict(width=1),
        fillcolor="rgba(5, 5, 5, 0.35)",
        fill="tonexty",
        showlegend=False,
    )
)

fig.update_layout(
    yaxis_title="{}".format(parameter), title="Reverberation Time", hovermode="x"
)

fig.show()

# Matplotlib
# fig = plt.figure()
# ax = plt.axes()
# ax.plot(thirds, reverberation_time)
# ax.set_xscale("log")
# ax.set_ylim(0, max(reverberation_time) * 1.1)
# plt.show()
