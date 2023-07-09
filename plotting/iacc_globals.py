"""Plots and computations for ASW and LEV"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly import figure_factory
import polars as pl
import seaborn as sns

from main import preprocess_dataframe

sheets_to_keep = ["ASW", "LEV"]
# data_dict = pd.read_excel("./data/data.xlsx", sheet_name=sheets_to_keep, encoding='latin1')
# asw_data = pd.read_csv("./data/ASW.csv", sep=";", header=0)
# lev_data = pd.read_csv("./data/LEV.csv", sep=";", header=0)
# asw_data = preprocess_dataframe(asw_data, "ASW")
# lev_data = preprocess_dataframe(asw_data, "LEV")

asw_pl = pl.read_csv("./data/ASW.csv", has_header=True, separator=";")
lev_pl = pl.read_csv("./data/LEV.csv", has_header=True, separator=";")


print(
    f"""
ASW mean: {asw_pl.select(pl.col("ASW").mean()).to_numpy().squeeze()}
ASW median: {asw_pl.select(pl.col("ASW").median()).to_numpy().squeeze()}
ASW standard deviation: {asw_pl.select(pl.col("ASW").std()).to_numpy().squeeze()}

LEV mean: {lev_pl.select(pl.col("LEV").mean()).to_numpy().squeeze()}
LEV median: {lev_pl.select(pl.col("LEV").median()).to_numpy().squeeze()}
LEV standard deviation: {lev_pl.select(pl.col("LEV").std()).to_numpy().squeeze()}
"""
# ASW MAD: {(asw_pl.select(pl.col("ASW")) - asw_pl.select(pl.col("ASW").median())).apply(lambda x: np.abs(x))}
# LEV MAD: {(lev_pl.select(pl.col("LEV")) - lev_pl.select(pl.col("LEV").median())).apply(lambda x: np.abs(x))}
)
exit()
# print(asw_data.describe())
# print(lev_data.describe())

# columns_to_keep = [
#     "measurement",
#     "distance",
#     "integration_time",
#     "parameter_x",
#     "parameter_y",
# ]
asw_data = asw_data.rename(columns={"ASW": "parameter"})
asw_data = asw_data.rename(
    columns={"ASW": "parameter"}
)  # fucking pandas needs this twice...
lev_data = lev_data.rename(columns={"LEV": "parameter"})
lev_data = lev_data.rename(columns={"LEV": "parameter"})  # motherfucking pandas
joint_df = pd.merge(
    left=asw_data,
    right=lev_data,
    on=["measurement", "distance", "integration_time"],
    how="outer",
    suffixes=("_left", "_right"),
)
joint_df = joint_df.rename(columns={"parameter_left": "ASW", "parameter_right": "LEV"})
joint_df = joint_df.rename(
    columns={"parameter_left": "ASW", "parameter_right": "LEV"}
)  # again, fucking pandas just in case
print(joint_df.describe())
print(
    "Spearman correlation between ASW and LEV:\n",
    joint_df[["ASW", "LEV"]].corr(method="spearman", min_periods=0),
)


def plot_scatter_2d(
    df: pd.DataFrame,
    parameter_name1: str,
    parameter_name2: str,
    parameter_units: str,
    show: bool = True,
    save: bool = False,
) -> None:
    BINS = 6
    fig = px.density_heatmap(
        df,
        x=parameter_name1,
        y=parameter_name2,
        nbinsx=BINS,
        nbinsy=BINS,
        # color="integration_time",
    )
    fig.update_layout(
        xaxis_title=f"{parameter_name1}",
        yaxis_title=f"{parameter_name2}",
    )
    if show:
        fig.show()
    if save:
        fig.write_image(f"./outputs/{parameter_name1}-vs-{parameter_name2}-heatmap.png")


plot_scatter_2d(joint_df, "ASW", "LEV", "", save=True)

fig = plt.figure()
ax = plt.gca()
sns.scatterplot(joint_df, x="ASW", y="LEV", hue="distance", ax=ax)
plt.show()
