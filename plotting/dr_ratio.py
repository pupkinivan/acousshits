import re
from traceback import print_exc

import plotly.express as px
import plotly.graph_objects as go
import polars as pl


def filter_integration_time(string: str):
    pattern = r".*((?P<integration_time>(350|100|10){1})ms)+.*"
    match = re.match(pattern, string, re.MULTILINE)
    try:
        return match.groupdict()["integration_time"]
    except:
        print_exc()
        raise ValueError(f"No match for integration time in {string}")


df_objective = pl.read_csv(
    "./data/results_LF-DR_objective.tsv", has_header=True, separator="\t"
).filter(pl.col("dr_ratio").is_not_nan() & pl.col("dr_ratio").is_not_null())

print(
    "Objective DR statistics:\n",
    df_objective.select(
        pl.col("dr_ratio").mean().alias("dr_ratio_mean"),
        pl.col("dr_ratio").std().alias("dr_ratio_std"),
    ),
)

df_subjective = (
    pl.read_csv("./data/results_LF-DR_subjective.tsv", has_header=True, separator="\t")
    .filter(pl.col("dr_ratio").is_not_nan() & pl.col("dr_ratio").is_not_null())
    .with_columns(
        pl.col("filename").apply(filter_integration_time).alias("integration_time")
    )
)

print(
    "Subjective DR statistics:\n",
    df_subjective.groupby("integration_time").agg(
        pl.col("dr_ratio").mean().alias("dr_ratio_mean"),
        pl.col("dr_ratio").std().alias("dr_ratio_std"),
    ),
)

def plot_dr_vs_distance(df: pl.DataFrame, dr_column: str, distance_column: str) -> None:    
    fig = px.line(df.to_numpy(), x=distance_column, y=dr_column)
    # fig.update_layout(title="", yaxis_title="", xaxis_title="")
    fig.show()

