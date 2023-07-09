import plotly.express as px
import plotly.graph_objects as go
import polars as pl

from main import likely_frequency_bands

df = pl.read_csv(
    "./data/SNR.csv",
    has_header=True,
    separator=";",
    dtypes={
        "Medición": pl.Utf8,
        "Posición": pl.Utf8,
        "Dist a fuente": pl.Float32,
        "T de integ": pl.Int16,
        "50": pl.Float32,
        "63": pl.Float32,
        "80": pl.Float32,
        "100": pl.Float32,
        "125": pl.Float32,
        "160": pl.Float32,
        "200": pl.Float32,
        "250": pl.Float32,
        "315": pl.Float32,
        "400": pl.Float32,
        "500": pl.Float32,
        "630": pl.Float32,
        "800": pl.Float32,
        "1000": pl.Float32,
        "1300": pl.Float32,
        "1600": pl.Float32,
        "2000": pl.Float32,
        "2500": pl.Float32,
        "3200": pl.Float32,
        "4000": pl.Float32,
        "5000": pl.Float32,
        "6300": pl.Float32,
        "8000": pl.Float32,
        "10000": pl.Float32,
        "12500": pl.Float32,
        "SNR": pl.Float32,
    },
)
df = df.with_columns(
    pl.col("Medición").alias("measurement"),
    pl.col("Posición").alias("microphone_position"),
    pl.col("Dist a fuente").alias("distance"),
    pl.col("T de integ").alias("integration_time"),
)

present_bands = [band for band in likely_frequency_bands if band in df.columns]

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


def plot_snr_per_band(
    df: pl.DataFrame, present_bands: list, save: bool = False, show: bool = False
) -> None:
    # statistics
    sorted_bands = sorted(list(map(lambda s: int(s), present_bands)))
    stds = []
    means = []
    rail_top = []
    rail_bottom = []
    for band in sorted_bands:
        std = df.select(pl.col(str(band)).std()).to_numpy().squeeze()
        stds.append(std)
        mean = df.select(pl.col(str(band)).mean()).to_numpy().squeeze()
        means.append(mean)
        rail_top.append(mean + std)
        rail_bottom.append(mean - std)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=sorted_bands, y=means, name="Mean"))
    fig.add_trace(
        go.Scatter(
            name="Mean + 1 StD",
            x=sorted_bands,
            y=rail_top,
            mode="lines",
            marker=dict(color="#000"),
            line=dict(width=0),
            showlegend=False,
        )
    )
    fig.add_trace(
        go.Scatter(
            name="Mean ± 1 StD",
            x=sorted_bands,
            y=rail_bottom,
            mode="lines",
            marker=dict(color="#000"),
            line=dict(width=0),
            fillcolor="rgba(5, 5, 5, 0.25)",
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
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor="DarkGrey")
    fig.update_layout(
        yaxis_title="SNR",
        title="SNR",
        hovermode="x",
        legend=dict(yanchor="top", y=0.95, xanchor="left", x=0.75),
    )
    
    if show:
        fig.show()
    if save:
        fig.write_image(f"./outputs/SNR.png")


plot_snr_per_band(df, present_bands, save=True, show=True)
