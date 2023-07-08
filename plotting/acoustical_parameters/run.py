"""Apply acoustical parameters to recorded RIR."""
import json
import os
from pathlib import Path
import re
from typing import Dict, List, Union

import numpy as np
import pandas as pd
from soundfile import read as sf_read

from plotting.acoustical_parameters import (
    direct_reverberant_ratio,
    get_direct_sound_arrival,
    lateral_fraction_early,
    lateral_fraction_late,
)
from plotting.utils import read_aformat, convert_ambisonics_a_to_b

input_directory = input(
    "Input directory? [/mnt/Ivan'sDrive/Documents/untref/materias/ima/final/RIRs/subjetivadas]: "
)
default_directory = (
    "/mnt/Ivan'sDrive/Documents/untref/materias/ima/final/RIRs/subjetivadas"
)
input_directory = Path(
    input_directory if input_directory != "" else default_directory
).resolve()

results_df = pd.DataFrame(
    {
        "measurement": [],
        "processing_type": [],
        "filename": [],
        "filepath": [],
        "direct_sound_arrival_ms": [],
        "lf_early": [],
        "lf_late": [],
        "dr_ratio": [],
    }
)

from multiprocessing import cpu_count, Pool

processing_pool = Pool(cpu_count() - 2)


def resolve_paths(base_directory: str, files: List[str]) -> List[Path]:
    merged_paths = []
    for filename in files:
        merged_paths.append((Path(base_directory) / filename).resolve())
    return merged_paths


def extract_acoustical_parameters_omni(file_path: Path):
    audio, sample_rate = sf_read(str(file_path))
    dr_ratio = direct_reverberant_ratio(audio, sample_rate)
    arrival_ms = get_direct_sound_arrival(audio, sample_rate, as_milliseconds=True)
    file_name = str(file_path).split("/")[-1]
    return {
        "position_id": extract_mic_number(file_name),
        "processing_type": "omni",
        "file_path": file_path,
        "file_name": file_name,
        "dr_ratio": dr_ratio,
        "direct_sound_arrival_ms": arrival_ms,
    }


def extract_acoustical_parameters_ambi(aformat_dict: dict):
    """_summary_

    Args:
        aformat_dict (dict): a dictionary with A-format capsule names as keys and filepath as value

    Returns
        No sé
    """
    aformat_rirs, sample_rate = read_aformat(
        [
            # 1. front left up
            # 2. front right down
            # 3. back left down
            # 4. back right up
            aformat_dict["front_left_up"],
            aformat_dict["front_right_down"],
            aformat_dict["back_left_down"],
            aformat_dict["back_right_up"],
        ]
    )
    bformat_rir = convert_ambisonics_a_to_b(*[aformat_rirs[i, :] for i in range(4)])
    lf_early = lateral_fraction_early(bformat_rir, sample_rate)
    lf_late = lateral_fraction_late(bformat_rir, sample_rate)
    dr_ratio = direct_reverberant_ratio(bformat_rir[0, :], sample_rate)
    direct_sound_arrival_ms = get_direct_sound_arrival(bformat_rir[0, :], sample_rate)
    return {
        "measurement_id": aformat_dict["measurement_id"],
        "processing_type": "ambi",
        "files": aformat_dict["files"],
        "lf_early": lf_early,
        "lf_late": lf_late,
        "dr_ratio": dr_ratio,
        "direct_sound_arrival_ms": direct_sound_arrival_ms,
    }


def merge_soundfield_mics(file_list: List[str], base_directory: Path = None):
    pattern = r"^(?P<mic_type>[a-zA-Z]+)\s(?P<mic_number>[1-4])+-(?P<position_id>[0-9]{1,2})[a-zA-Z0-9_-]*.wav"
    aformat_files = dict()
    mic_number_to_direction = {
        "1": "front_left_up",
        "2": "front_right_down",
        "3": "back_left_down",
        "4": "back_right_up",
    }
    for filename in file_list:
        match = re.match(pattern, filename)
        if match:
            match_group_dict = match.groupdict()
            mic_type = match_group_dict["mic_type"]
            position_id = match_group_dict["position_id"]
            if mic_type.lower() != "soundfield":
                continue
            mic_capsule = mic_number_to_direction[match_group_dict["mic_number"]]
            if position_id not in set(aformat_files.keys()):
                aformat_files[position_id] = {
                    "measurement_id": position_id,
                    "files": [filename],
                }
            aformat_files[position_id].update(
                {
                    mic_capsule: filename
                    if not base_directory
                    else base_directory / filename,
                    "files": set(
                        list(aformat_files[position_id]["files"]) + [filename]
                    ),
                }
            )
    return aformat_files


def extract_mic_number(file_name: str) -> str:
    pattern = r"Earthworks\s(?P<mic_number>[0-9])+-[a-zA-Z0-9_-]+.wav"
    match = re.match(pattern, file_name)
    if match:
        match_group_dict = match.groupdict()
        mic_number = match_group_dict["mic_number"]
        return mic_number


def map_omni_result_to_row(omni_result: dict, measurement_id: str) -> pd.Series:
    return pd.Series(
        {
            "measurement": measurement_id,
            "processing_type": "omni",
            "filename": omni_result["file_name"],
            "filepath": omni_result["file_path"],
            "direct_sound_arrival_ms": omni_result["direct_sound_arrival_ms"],
            "lf_early": None,
            "lf_late": None,
            "dr_ratio": omni_result["dr_ratio"],
        }
    )


def map_ambi_result_to_row(ambi_result: dict, measurement_id: str) -> pd.Series:
    return pd.Series(
        {
            "measurement": measurement_id,
            "processing_type": "ambi",
            "filename": ",".join(ambi_result["files"]),
            "filepath": ",".join(ambi_result["files"]),
            "direct_sound_arrival_ms": ambi_result["direct_sound_arrival_ms"],
            "lf_early": ambi_result["lf_early"],
            "lf_late": ambi_result["lf_late"],
            "dr_ratio": ambi_result["dr_ratio"],
        }
    )


def extract_acoustical_parameters(recording: Union[Path, dict]) -> pd.Series:
    print("Processing {}".format(recording))
    if isinstance(recording, dict):
        return extract_acoustical_parameters_ambi(recording)
    elif isinstance(recording, Path):
        return extract_acoustical_parameters_omni(recording)
    else:
        raise ValueError(
            "Expected an argument of type dict or Path, not {}".format(type(recording))
        )


def map_acoustical_parameters_to_row(
    acoustical_parameters: dict, measurement_id: str
) -> pd.Series:
    if acoustical_parameters["processing_type"] == "ambi":
        dataframe_row = map_ambi_result_to_row(acoustical_parameters, measurement_id)
        return dataframe_row
    elif acoustical_parameters["processing_type"] == "omni":
        dataframe_row = map_omni_result_to_row(acoustical_parameters, measurement_id)
        return dataframe_row


def extract_measurement_number(string: str) -> str:
    pattern = r".*medicion([0-9]+)"
    match = re.match(pattern, string)
    if match is None:
        print("WARNING: could not find numbers in string {}".format(string))
        return string
    return match.groups()[0]


for i, walk_tuple in enumerate(os.walk(input_directory)):
    if i == 0:
        measurements = walk_tuple[1]
        print(f"Measurements:\n{measurements}")
        continue

    if len(walk_tuple[-1]) > 0:
        measurement_id = extract_measurement_number(walk_tuple[0])

        soundfield_mics = [
            capsules_dict
            for capsules_dict in merge_soundfield_mics(
                walk_tuple[-1],
                Path(walk_tuple[0]),
            ).values()
        ]
        other_mics = [
            Path(walk_tuple[0]) / filename
            for filename in walk_tuple[-1]
            if "Earthworks" in filename
        ]
        all_mics: list = other_mics + soundfield_mics
        # print("All mics:")
        # [print("{}".format(str(mic))) for mic in all_mics]

        # results_awaitable = processing_pool.map_async(extract_acoustical_parameters, all_mics)
        # for mic_parameters_result in results_awaitable.get():
        #     results_df = pd.concat(results_df, mic_parameters_result)
        for mic in all_mics:
            acoustical_parameters = extract_acoustical_parameters(mic)
            row = map_acoustical_parameters_to_row(
                acoustical_parameters, measurement_id
            )
            results_df = pd.concat(
                [results_df, row.to_frame().T], axis=0, ignore_index=True
            )

results_df.to_csv(input_directory / "results.tsv", sep="\t", index=False)
