"""Entrypoint"""
import logging

import pandas as pd

from plotting.plots import (
    plot_lines_with_distance,
    plot_lines_with_integration_time,
    plot_iacc_with_integration_time,
    plot_boxplot,
)

SAVE = False
SHOW = False

logging.basicConfig(level=logging.INFO)

# Done:
# Ts por zona
# EDT por zona
# T20 por zona
# T30 por zona
# C50 por zona
# C80 por zona
# Ts subjetivo
# EDT subjetivo
# T20 subjetivo
# T30 subjetivo
# C50 subjetivo
# C80 subjetivo

#

# TODO: Missing
# - STI
# - SNR
# - St1, St2
# - ASW
# - LEV
# - LFearly objetivo
# - LFlate objetivo
# - DR objetivo
# - LFearly subjetivo
# - LFlate subjetivo
# - DR subjetivo
# - IACC
# - IACC por octava

sheets_to_keep = {
    "STI": "STI male/female",  # single number, boxplot
    "SNR": "SNR",
    "Ts": "Ts",
    "EDT": "EDT",
    "T20": "T20",
    "T30": "T30",
    "C50": "C50",
    "C80": "C80",
    # "G": "G",
    "ST param": "St1,St2",  # thirds starting from 5; plot separately
    "IACC": "IACC",  # extra: full/early/late; thirds starting from 5. plot early/late/all separately; no seat position. compare integration time.
    "IACC oct": "{} per octave",  # extra: early/late; OCTAVES starting from 5; no seat position. compare integration time.
    "ASW": "ASW",  # last col; no seat position. compare integration time.
    "LEV": "LEV",  # last col; no seat position. compare integration time.
    "LF y DR objetivas": "LF_early,LF_late,DR",  # LF early, LF late y DR
    "LF y DR subjetivas": "LF_early_subjective,LF_late_subjective,DR_subjective",  # LF early, LF late y DR
}

parameters_to_units = {
    "STI male/female": "",
    "SNR": "dB",
    "Ts": "s",
    "EDT": "s",
    "T20": "s",
    "T30": "s",
    "C50": "dB",
    "C80": "dB",
    "IACC": "",
    "{} per octave": "",
    "ASW": "",
    "LEV": "",
    "St1,St2": "dB",
    "LF_early,LF_late,DR": "dB",
    "LF_early_subjective,LF_late_subjective,DR_subjective": "dB",
}

plot_group1 = [
    "SNR",  # <- FIXME: no aparece la curva
    "Ts",
    "EDT",
    "T20",
    "T30",
    "C50",
    "C80",
]

plot_group_iacc = [
    "IACC",
    "IACC oct",
]

plot_group_iacc_globals = [
    "ASW",
    "LEV",
]


likely_frequency_bands = [
    "500",
    "1,000",
    "1,300",
    "1,600",
    "2,000",
    "2,500",
    "3,200",
    "4,000",
    "5,000",
    "6,300",
    "8,000",
    "10,000",
    "12,500",
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
    50,
    63,
    80,
    100,
    125,
    160,
    200,
    250,
    315,
    400,
    500,
    630,
    800,
    1000,
    2000,
    1000,
    1300,
    1600,
    2000,
    2500,
    3200,
    4000,
    5000,
    6300,
    8000,
    10000,
    12500,
    1.000,
    1.300,
    1.600,
    2.000,
    2.500,
    3.200,
    4.000,
    5.000,
    6.300,
    8.000,
    10.000,
    12.500,
]


def read_data_file():
    return pd.read_excel("./data/data.xlsx", sheet_name=list(sheets_to_keep.keys()))


def preprocess_dataframe(df: pd.DataFrame, parameter_name: str) -> pd.DataFrame:
    df = df.rename(
        columns={
            "Medición": "measurement",
            "Posición": "microphone_position",
            "Dist a fuente": "distance",
            "T de integ": "integration_time",
            "Integration time": "integration_time",
            "Temporalidad": "iacc_type",
        }
    )
    for numerical_column in likely_frequency_bands:
        if numerical_column in df:
            df[numerical_column] = pd.to_numeric(df[numerical_column], errors="raise")
    if parameter_name in df:
        df[parameter_name] = pd.to_numeric(df[parameter_name], errors="raise")
    if (number_of_nans := df.isna().any(axis=1).sum()) > 0:
        logging.error(
            "{:}/{:} rows are NaN in sheet for parameter {} ({:4.2f}%); skipping its plots...".format(
                number_of_nans, len(df), parameter_name, 100 * number_of_nans / len(df)
            )
        )
    return df


def plot_df_in_group1(df: pd.DataFrame, parameter: str, units: str):
    df = df[df["measurement"] != 7]
    logging.info("Plotting %s", parameter)
    plot_lines_with_distance(df, parameter, units, 4, show=SHOW, save=SAVE)
    plot_lines_with_integration_time(df, parameter, units, 4, show=SHOW, save=SAVE)
    logging.info("Finished plotting %s", parameter)


def plot_iacc(df: pd.DataFrame, parameter: str, units: str):
    for iacc_type in df["iacc_type"].unique().squeeze().tolist():
        df_filtered = df[df["iacc_type"] == iacc_type]
        iacc_name = parameter.format(iacc_type)
        logging.info("Plotting %s", iacc_name)
        plot_iacc_with_integration_time(
            df_filtered, iacc_name, units, 5, save=SAVE, show=SHOW
        )


def plot_global(df: pd.DataFrame, parameter: str, units: str):
    logging.info("Plotting %s", parameter)
    plot_boxplot(df, parameter, units, parameter, show=True, save=True)


def main():
    df_dict = read_data_file()

    for sheet_name, df in df_dict.items():
        parameter_name = sheets_to_keep[sheet_name]
        parameter_units = parameters_to_units[parameter_name]
        df = preprocess_dataframe(df, parameter_name)

        if sheet_name in plot_group1:
            continue
            plot_df_in_group1(df, parameter_name, parameter_units)
        elif sheet_name in plot_group_iacc:
            continue
            plot_iacc(df, parameter_name, parameter_units)
        elif parameter_name in plot_group_iacc_globals:
            plot_global(df, parameter_name, parameter_units)
        else:
            logging.warning(
                "Plotting for parameter %s not implemented yet; skipping...",
                parameter_name,
            )
            continue


if __name__ == "__main__":
    main()
