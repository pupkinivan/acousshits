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
)
df_objective = df_objective.filter(
    pl.col("lf_early").is_not_nan()
    & pl.col("lf_early").is_not_null()
    & pl.col("lf_late").is_not_nan()
    & pl.col("lf_late").is_not_null()
)

print(
    "Objective LFs statistics:\n",
    df_objective.select(
        pl.col("lf_early").mean().alias("lf_early_mean"),
        pl.col("lf_early").std().alias("lf_early_std"),
        pl.col("lf_late").mean().alias("lf_late_mean"),
        pl.col("lf_late").std().alias("lf_late_std"),
    )
)

df_subjective = (
    pl.read_csv("./data/results_LF-DR_subjective.tsv", has_header=True, separator="\t")
    .filter(
        pl.col("lf_early").is_not_nan()
        & pl.col("lf_early").is_not_null()
        & pl.col("lf_late").is_not_nan()
        & pl.col("lf_late").is_not_null()
    )
    .with_columns(
        pl.col("filename").apply(filter_integration_time).alias("integration_time")
    )
)

print(
    "Subjective LFs statistics:\n",
    df_subjective.groupby("integration_time").agg(
        pl.col("lf_early").mean().alias("lf_early_mean"),
        pl.col("lf_early").std().alias("lf_early_std"),
        pl.col("lf_late").mean().alias("lf_late_mean"),
        pl.col("lf_late").std().alias("lf_late_std"),
    )
)
