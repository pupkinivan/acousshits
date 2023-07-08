from random import random

import pandas as pd
from plotly import graph_objects as go
import plotly.express as px


valid_frequencies = [
    "50",
    "63",
    "80",
    "100",
    "125",
    "160",
    "200",
    "250",
    "315",
    "400",
    "500",
    "630",
    "800",
    "1000",
    "1300",
    "1600",
    "2000",
    "2500",
    "3200",
    "4000",
    "5000",
    "6300",
    "8000",
    "10000",
    "12500",
]

# Microphone zones
zone1 = [2, 3]
zone2 = [
    1,
    5,
    6,
    7,
]
zone3 = [8, 9, 10, 11]
zone4 = [12, 13, 14]
zones = (zone1, zone2, zone3, zone4)

integration_times = (10, 100, 350)


def plot_iacc_with_integration_time(
    df: pd.DataFrame,
    parameter_name: str,
    parameter_units: str,
    frequency_column_start: int,
    show: bool = True,
    save: bool = False,
):
    # Compute global statistics first
    bands = [
        column_name
        for column_name in df.columns[frequency_column_start:]
        if str(column_name) in valid_frequencies
    ]
    rails_top = []
    rails_bottom = []
    general_mean = []
    for freq in bands:
        rails_top.append(df[freq].mean() + 1 * df[freq].std())
        rails_bottom.append(df[freq].mean() - 1 * df[freq].std())
        general_mean.append(df[freq].mean())

    # Plot mean for each integration time group
    fig = go.Figure().update_layout(template="plotly_white")
    for integration_time in df["integration_time"].unique().squeeze().tolist():
        means = [
            df[df["integration_time"] == integration_time][freq].mean()
            for freq in bands
        ]
        fig.add_trace(
            go.Scatter(
                name="Mean integrating {} ms".format(integration_time),
                x=bands,
                y=means,
                mode="lines",
                # marker=dict(color="#000"),
                line=dict(width=1.5),
            )
        )

    # Add top and bottom rails, and fill the area inbetween
    fig.add_trace(
        go.Scatter(
            name="Global mean + 1 StD",
            x=bands,
            y=rails_top,
            mode="lines",
            marker=dict(color="#000"),
            line=dict(width=0),
            showlegend=False,
        )
    )
    fig.add_trace(
        go.Scatter(
            name="Global mean - 1 StD",
            x=bands,
            y=rails_bottom,
            mode="lines",
            marker=dict(color="#000"),
            line=dict(width=0),
            fillcolor="rgba(5, 5, 5, 0.25)",
            fill="tonexty",
            showlegend=False,
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
        yaxis_title=f"{parameter_name}",
        title=parameter_name,
        hovermode="x",
        legend=dict(yanchor="top", y=0.95, xanchor="left", x=0.65),
    )
    if show:
        fig.show()
    if save:
        fig.write_image(f"./outputs/{parameter_name}-with-integration-time.png")


def plot_lines_with_integration_time(
    df: pd.DataFrame,
    parameter_name: str,
    parameter_units: str,
    frequency_column_start: int,
    show: bool = True,
    save: bool = False,
):
    # Compute global statistics first
    bands = [
        column_name
        for column_name in df.columns[frequency_column_start:]
        if str(column_name) in valid_frequencies
    ]
    rails_top = []
    rails_bottom = []
    general_mean = []
    for freq in bands:
        rails_top.append(df[freq].mean() + 1 * df[freq].std())
        rails_bottom.append(df[freq].mean() - 1 * df[freq].std())
        general_mean.append(df[freq].mean())

    # Plot mean for each integration time group
    fig = go.Figure().update_layout(template="plotly_white")
    for integration_time in integration_times:
        means = [
            df[df["integration_time"] == integration_time][freq].mean()
            for freq in bands
        ]
        fig.add_trace(
            go.Scatter(
                name="Mean integrating {} ms".format(integration_time),
                x=bands,
                y=means,
                mode="lines",
                # marker=dict(color="#000"),
                line=dict(width=1.5),
            )
        )

    # Add top and bottom rails, and fill the area inbetween
    fig.add_trace(
        go.Scatter(
            name="Global mean + 1 StD",
            x=bands,
            y=rails_top,
            mode="lines",
            marker=dict(color="#000"),
            line=dict(width=0),
            showlegend=False,
        )
    )
    fig.add_trace(
        go.Scatter(
            name="Global mean - 1 StD",
            x=bands,
            y=rails_bottom,
            mode="lines",
            marker=dict(color="#000"),
            line=dict(width=0),
            fillcolor="rgba(5, 5, 5, 0.25)",
            fill="tonexty",
            showlegend=False,
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
        yaxis_title=f"{parameter_name} [{parameter_units}]",
        title=parameter_name,
        hovermode="x",
        legend=dict(yanchor="top", y=0.95, xanchor="left", x=0.65),
    )
    if show:
        fig.show()
    if save:
        fig.write_image(f"./outputs/{parameter_name}-with-integration-time.png")


def plot_lines_with_distance(
    df: pd.DataFrame,
    parameter_name: str,
    parameter_units: str,
    frequency_column_start: int,
    show: bool = True,
    save: bool = False,
):
    # Compute global statistics first
    bands = [
        column_name
        for column_name in df.columns[frequency_column_start:]
        if str(column_name) in valid_frequencies
    ]
    rails_top = []
    rails_bottom = []
    general_mean = []
    for freq in bands:
        rails_top.append(df[freq].mean() + 1 * df[freq].std())
        rails_bottom.append(df[freq].mean() - 1 * df[freq].std())
        general_mean.append(df[freq].mean())

    # Plot mean for each zone group
    last_distance = 0
    fig = go.Figure().update_layout(template="plotly_white")
    for i, zone in enumerate(zones):
        means = [
            df[df["microphone_position"].isin(zone)][freq].mean() for freq in bands
        ]
        fig.add_trace(
            go.Scatter(
                name="Mean for zone {}".format(i + 1),
                x=bands,
                y=means,
                mode="lines",
                # marker=dict(color="#000"),
                line=dict(width=1.5),
            )
        )

    # Add top and bottom rails, and fill the area inbetween
    fig.add_trace(
        go.Scatter(
            name="Global mean + 1 StD",
            x=bands,
            y=rails_top,
            mode="lines",
            marker=dict(color="#000"),
            line=dict(width=0),
            showlegend=False,
        )
    )
    fig.add_trace(
        go.Scatter(
            name="Global mean - 1 StD",
            x=bands,
            y=rails_bottom,
            mode="lines",
            marker=dict(color="#000"),
            line=dict(width=0),
            fillcolor="rgba(5, 5, 5, 0.25)",
            fill="tonexty",
            showlegend=False,
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
        yaxis_title=f"{parameter_name} [{parameter_units}]",
        title=parameter_name,
        hovermode="x",
        legend=dict(yanchor="top", y=0.95, xanchor="left", x=0.75),
    )
    if show:
        fig.show()
    if save:
        fig.write_image(f"./outputs/{parameter_name}-with-distance.png")


def plot_boxplot(
    df: pd.DataFrame,
    parameter_name: str,
    parameter_units: str,
    parameter_column: str,
    show: bool = True,
    save: bool = False
) -> None:
    fig = px.box(df, x="integration_time", y=parameter_column)
    # fig.update_layout(
    #     yaxis_title=f"{parameter_name}""
    # )
    if show:
        fig.show()
    if save:
        fig.write_image(f"./outputs/{parameter_name}-boxplot.png")