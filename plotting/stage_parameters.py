import plotly.express as px
import plotly.graph_objects as go
import polars as pl

from main import likely_frequency_bands

# df = pl.read_csv(
#     "./data/SNR.csv",
#     has_header=True,
#     separator=";",
#     dtypes={
#         "Medición": pl.Utf8,
#         "Posición": pl.Utf8,
#         "Dist a fuente": pl.Float32,
#         "Integration time": pl.Int16,
#         "Frq.band [Hz]": pl.Utf8,
#         "50": pl.Float32,
#         "63": pl.Float32,
#         "80": pl.Float32,
#         "100": pl.Float32,
#         "125": pl.Float32,
#         "160": pl.Float32,
#         "200": pl.Float32,
#         "250": pl.Float32,
#         "315": pl.Float32,
#         "400": pl.Float32,
#         "500": pl.Float32,
#         "630": pl.Float32,
#         "800": pl.Float32,
#         "1,000": pl.Float32,
#         "1,300": pl.Float32,
#         "1,600": pl.Float32,
#         "2,000": pl.Float32,
#         "2,500": pl.Float32,
#         "3,200": pl.Float32,
#         "4,000": pl.Float32,
#         "5,000": pl.Float32,
#         "6,300": pl.Float32,
#         "8,000": pl.Float32,
#         "10,000": pl.Float32,
#         "12,500": pl.Float32,
#         "Promedio": pl.Float32,
#     },
# )
df = pl.read_excel("./data/data.xlsx", sheet_name="ST param")
df = df.with_columns(
    pl.col("Medición").alias("measurement"),
    pl.col("Posición").alias("microphone_position"),
    pl.col("Dist a fuente").alias("distance"),
    pl.col("Integration time").alias("integration_time"),
    pl.col("Frq.band [Hz]").alias("parameter"),
)

present_bands = [band for band in likely_frequency_bands if band in df.columns]

# all_max = df.select(*[pl.col(col) for col in present_bands]).max().max().to_numpy().squeeze()[0]
# all_min = df.select(*[pl.col(col) for col in present_bands]).min().min().to_numpy().squeeze()[0]
# y_max = 0.9*all_max if all_max > 0 else 1.1*all_max
# y_min = 0.9*all_min if all_min > 0 else 1.1*all_min

# statistics = df.select(
#     *[
#         pl.mean(col).alias(f"avg({col})")
#         for col in df.columns
#         if col in likely_frequency_bands
#     ],
#     *[
#         pl.median(col).alias(f"median({col})")
#         for col in df.columns
#         if col in likely_frequency_bands
#     ],
#     *[
#         pl.std(col).alias(f"std({col})")
#         for col in df.columns
#         if col in likely_frequency_bands
#     ],
#     *[
#         (pl.col(col) - pl.median(col)).abs().alias(f"mad({col})")
#         for col in df.columns
#         if col in likely_frequency_bands
#     ],
# )
# print(statistics)

# pivotted = df.melt(
#     id_vars=["measurement", "microphone_position", "integration_time"],
#     value_vars=present_bands,
# )
# print(pivotted)


def plot_stage_parameters_per_band(
    df: pl.DataFrame, present_bands: list, group: str, save: bool = False, show: bool = False
) -> None:
    means = df.groupby("parameter").agg(
        *[pl.col(col).mean().alias(col) for col in present_bands]
    )
    stds = df.groupby("parameter").agg(
        *[pl.col(col).std().alias(col) for col in present_bands]
    )
    rail_top_st1 = (
        means.filter(pl.col("parameter") == "St1")
        .drop("parameter")[0]
        .to_numpy()
        .squeeze()
        + stds.filter(pl.col("parameter") == "St1")
        .drop("parameter")[0]
        .to_numpy()
        .squeeze()
    )
    rail_bottom_st1 = (
        means.filter(pl.col("parameter") == "St1")
        .drop("parameter")[0]
        .to_numpy()
        .squeeze()
        - stds.filter(pl.col("parameter") == "St1")
        .drop("parameter")[0]
        .to_numpy()
        .squeeze()
    )
    rail_top_st2 = (
        means.filter(pl.col("parameter") == "St2")
        .drop("parameter")[0]
        .to_numpy()
        .squeeze()
        + stds.filter(pl.col("parameter") == "St2")
        .drop("parameter")[0]
        .to_numpy()
        .squeeze()
    )
    rail_bottom_st2 = (
        means.filter(pl.col("parameter") == "St2")
        .drop("parameter")[0]
        .to_numpy()
        .squeeze()
        - stds.filter(pl.col("parameter") == "St2")
        .drop("parameter")[0]
        .to_numpy()
        .squeeze()
    )

    fig = go.Figure()

    # Plot means
    fig.add_trace(
        go.Scatter(
            x=means.columns[1:],
            y=means.filter(pl.col("parameter") == "St1")
            .drop("parameter")[0]
            .to_numpy()
            .squeeze(),
            name="Mean St1",
            mode="lines",
            marker=dict(color="#00F"),
        )
    )

    fig.add_trace(
        go.Scatter(
            x=means.columns[1:],
            y=means.filter(pl.col("parameter") == "St2")
            .drop("parameter")[0]
            .to_numpy()
            .squeeze(),
            name="Mean St2",
            mode="lines",
            marker=dict(color="#F00"),
        )
    )

    # Plot shaded areas
    fig.add_trace(
        go.Scatter(
            name="shade mean(st1)+std(st1)",
            x=means.columns[1:],
            y=rail_top_st1,
            mode="lines",
            marker=dict(color="#11F"),
            line=dict(width=0),
            showlegend=False,
        )
    )
    fig.add_trace(
        go.Scatter(
            name="Mean(St1) ± StD(St1)",
            x=means.columns[1:],
            y=rail_bottom_st1,
            mode="lines",
            marker=dict(color="#11F"),
            line=dict(width=0),
            fillcolor="rgba(1, 1, 255, 0.25)",
            fill="tonexty",
            showlegend=True,
        )
    )
    fig.add_trace(
        go.Scatter(
            name="shade mean(st2)+std(st2)",
            x=means.columns[1:],
            y=rail_top_st2,
            mode="lines",
            marker=dict(color="#F11"),
            line=dict(width=0),
            showlegend=False,
        )
    )
    fig.add_trace(
        go.Scatter(
            name="Mean(St2) ± StD(St2)",
            x=means.columns[1:],
            y=rail_bottom_st2,
            mode="lines",
            marker=dict(color="#F11"),
            line=dict(width=0),
            fillcolor="rgba(255, 1, 1, 0.25)",
            fill="tonexty",
            showlegend=True,
        )
    )

    fig.update_xaxes(
        title="Frequency [Hz]",
        type="log",
        showgrid=True,
        gridwidth=1,
        gridcolor="DarkGrey",
    )
    fig.update_yaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor="DarkGrey",
        # range=[y_min, y_max],
    )
    fig.update_layout(
        yaxis_title="St1 and St2",
        title=f"Stage Parameters 1 and 2, integrated in {group} ms",
        hovermode="x",
        legend=dict(yanchor="top", y=0.95, xanchor="left", x=0.65),
    )

    if show:
        fig.show()
    if save:
        fig.write_image(f"./outputs/stage-parameters-integration{group}.png")


for integration_time in (10, 100, 350):
    plot_stage_parameters_per_band(
        df.filter(pl.col("integration_time") == integration_time),
        present_bands,
        str(integration_time),
        save=True,
        show=True,
    )
