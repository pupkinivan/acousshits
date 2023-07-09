"""Audio IO and Ambisonics formatting utilities"""

from functools import singledispatch
from pathlib import Path
from traceback import print_exc
from typing import Dict, List, Tuple, Union

import numpy as np
import soundfile as sf


def read_signals_dict(signals_dict: dict) -> dict:
    """Read the signals contained in signals_dict and overwrites the paths with the arrays.

    Parameters
    ----------
    signals_dict : dict
        Dictionary with signals path.

    Returns
    -------
    dict
        Same signals_dict dictionary with the signals array overwritting signals path.
    """
    for key_i, path_i in signals_dict.items():
        try:  # a puro huevo
            signal_i, sample_rate = sf.read(path_i)
            signals_dict[key_i] = signal_i.T
        except:
            pass
    signals_dict["sample_rate"] = sample_rate

    if signals_dict["channels_per_file"] == 1:
        if signals_dict["input_mode"] == "bformat":
            bformat_keys = ["w_channel", "x_channel", "y_channel", "z_channel"]
            signals_dict["stacked_signals"] = stack_dict_arrays(
                signals_dict, bformat_keys
            )
        else:
            aformat_keys = [
                "front_left_up",
                "front_right_down",
                "back_right_up",
                "back_left_down",
            ]
            signals_dict["stacked_signals"] = stack_dict_arrays(
                signals_dict, aformat_keys
            )

    return signals_dict


def stack_dict_arrays(signals_dict_array: dict, keys: List[str]) -> np.ndarray:
    """Stacks arrays into single numpy.ndarray object given the dictionary and the keys
    to be stacked.

    Parameters
    ----------
    signals_dict_array : dict
        Dictionary containing the arrays to be stacked
    keys : List[str]
        Keys of signals_dict_array with the arrays to be stacked

    Returns
    -------
    np.ndarray
        Stacked arrays into single numpy.ndarray object
    """
    audio_array = []
    for key_i in keys:
        audio_array.append(signals_dict_array[key_i])

    return audio_array


@singledispatch
def read_aformat(audio_path: Union[str, Path]) -> Tuple[np.ndarray, float]:
    """Read an A-format Ambisonics signal from a single audio path, which is expected
    to contain 4 channels.

    Parameters
    ----------
    audio_paths : str | Path
        Strings containing the audio paths to be loaded

    Returns
    -------
    Tuple[np.ndarray, float]
        Sample rate of the audios and audios loaded as rows of a np.ndarray
    """
    signal, sample_rate = sf.read(audio_path)
    signal = signal.T
    assert signal.shape[0] == 4, (
        f"Audio file {str(audio_path)} with shape {signal.shape} does not"
        f"contain 4 channels, so it cannot be A-format Ambisonics"
    )
    return signal, sample_rate


@read_aformat.register(list)
def _(audio_paths: List[str]) -> Tuple[np.ndarray, float]:
    """Read an A-format Ambisonics signal from audio paths. 4 paths are expected,
    one for each cardioid signal, in the following order:
        1. front left up
        2. front right down
        3. back right up
        4. back left down

    Parameters
    ----------
    audio_paths : List[str]
        Strings containing the audio paths to be loaded

    Returns
    -------
    Tuple[np.ndarray, float]
        Sample rate of the audios and audios loaded as rows of a np.ndarray
    """
    assert (isinstance(audio_paths, (str, Path, list))) or (
        len(audio_paths) in (1, 4)
    ), "One wave file with 4 channels or a list of 4 wave files is expected"

    audio_array = []
    for audio_i in audio_paths:
        try:
            audio_array_i, sample_rate = sf.read(audio_i)
            audio_array.append(audio_array_i)
        except sf.SoundFileError:
            print_exc()

    return np.array(audio_array), sample_rate


@read_aformat.register(dict)
def _(audio_paths: Dict[str, str]) -> Tuple[np.ndarray, float]:
    """Read an A-format Ambisonics signal from a dictionary with audio paths. 4 keys are expected,
    one for each cardioid signal:
        1. front_left_up
        2. front_right_down
        3. back_right_up
        4. back_left_down

    Parameters
    ----------
    audio_paths : Dict[str]
        Key-value pair containing the audio paths to be loaded for each FLU/FRD/BRU/BLD channel

    Returns
    -------
    Tuple[np.ndarray, float]
        Sample rate of the audios and audios loaded as rows of a np.ndarray
    """
    ordered_aformat_channels = (
        "front_left_up",
        "front_right_down",
        "back_right_up",
        "back_left_down",
    )  # Assert the ordering is standardized across the project
    try:
        audio_data = {
            cardioid_channel: dict(zip(("signal", "sample_rate"), sf.read(path)))
            for cardioid_channel, path in audio_paths.items()
        }

        # refactor from here
        audio_signals = [
            audio_data[channel_name]["signal"]
            for channel_name in ordered_aformat_channels
        ]
        sample_rates = [
            audio_data[channel_name]["sample_rate"]
            for channel_name in ordered_aformat_channels
        ]
        assert len(set(sample_rates)) == 1, "Multiple different sample rates were found"

        signals_array = np.array(audio_signals)
        return signals_array, sample_rates[0]
    except sf.SoundFileError:
        print_exc()


@singledispatch
def convert_ambisonics_a_to_b(
    front_left_up: np.ndarray,
    front_right_down: np.ndarray,
    back_left_down: np.ndarray,
    back_right_up: np.ndarray,
) -> np.ndarray:
    """Converts Ambisonics A-format to B-format

    Parameters
    ----------
    front_left_up : np.ndarray
            Front Left Up signal from A-format
    front_right_down : np.ndarray
        Front Right Down signal from A-format
    back_right_up : np.ndarray
        Back Right Up signal from A-format
    back_left_down : np.ndarray
        Back Left Down signal from A-format

    Returns
    -------
    np.ndarray
        B-format outputs (W, X, Y, Z)
    """

    front = front_left_up + front_right_down
    back = back_left_down + back_right_up
    left = front_left_up + back_left_down
    right = front_right_down + back_right_up
    up = front_left_up + back_right_up  # pylint: disable=invalid-name
    down = front_right_down + back_left_down

    w_channel = front + back
    x_channel = front - back
    y_channel = left - right
    z_channel = up - down

    return np.array([w_channel, x_channel, y_channel, z_channel])


@convert_ambisonics_a_to_b.register(list)
def _(aformat_channels: List[np.ndarray]) -> np.ndarray:
    """Converts Ambisonics A-format to B-format.

    Parameters
    ----------
    aformat_channels : List[np.ndarray]
        A list containing the 4 channels of A-format Ambisonics in the following order:
            1. Front Left Up
            2. Front Right Down
            3. Back Left Down
            4. Back Right Up

    Returns
    -------
    np.ndarray
        B-format outputs (W, X, Y, Z)
    """
    assert (
        len(aformat_channels) == 4
    ), "Conversion from A-format to B-format requires 4 channels"
    return convert_ambisonics_a_to_b.dispatch(np.ndarray)(
        front_left_up=aformat_channels[0],
        front_right_down=aformat_channels[1],
        back_left_down=aformat_channels[2],
        back_right_up=aformat_channels[3],
    )


def convert_polar_to_cartesian(
    radius: Union[float, np.ndarray],
    azimuth: Union[float, np.ndarray],
    elevation: Union[float, np.ndarray],
) -> Tuple[Union[float, np.ndarray]]:
    """Convert three 3D polar coordinates to Cartesian ones.

    Parameters
        radius: float | np.ndarray. The radii (or rho).
        azimuth: float | np.ndarray. The azimuth (also called theta or alpha).
        elevation: float | np.ndarray. The elevation (also called phi or polar).

    Returns
        (x, y, z): Tuple[float | np.ndarray]. The corresponding Cartesian coordinates.
    """
    return (
        radius * np.cos(azimuth) * np.sin(elevation),
        radius * np.sin(azimuth) * np.sin(elevation),
        radius * np.cos(elevation),
    )
