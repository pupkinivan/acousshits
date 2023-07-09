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

df = pl.read_excel("./data/data.xlsx", sheet_name="STI")  #, xlsx2csv_options={"separator": ';', "has_header": True})

df = df.with_columns(
    pl.col("Medición").alias("measurement"),
    pl.col("Dist a fuente").alias("distance"),
)

print(
    f"""
STI mean: {df.select(pl.col("STI").mean()).to_numpy().squeeze()}
STI median: {df.select(pl.col("STI").median()).to_numpy().squeeze()}
STI standard deviation: {df.select(pl.col("STI").std()).to_numpy().squeeze()}
"""
)