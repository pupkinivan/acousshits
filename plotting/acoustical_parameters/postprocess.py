from pathlib import Path
import pandas as pd

base_path = Path("/mnt/Ivan'sDrive/Documents/untref/materias/ima/final/RIRs/objetivas")

df = pd.read_csv(base_path / "results_objetivas.csv")
measurements = df["measurement_id"].unique().tolist()
for measurement_id in measurements:
    df[df["measurement_id"] == measurement_id].to_csv(
        base_path / "results_measurement{}.csv".format(measurement_id)
    )

base_path = Path("/mnt/Ivan'sDrive/Documents/untref/materias/ima/final/RIRs/subjetivas")

df = pd.read_csv(base_path / "results_subjetivas.csv")
measurements = df["measurement_id"].unique().tolist()
for measurement_id in measurements:
    df[df["measurement_id"] == measurement_id].to_csv(
        base_path / "results_measurement{}.csv".format(measurement_id)
    )
