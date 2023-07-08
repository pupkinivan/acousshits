"""Acoustical parameters"""
from typing import Optional, Union

import numpy as np
from scipy.signal import find_peaks

from plotting.utils import convert_ambisonics_a_to_b
from plotting.utils import read_aformat


def seconds_to_samples(seconds: float, sample_rate: int) -> int:
    """Compute how many samples a number of seconds equals.

    Args:
        seconds (int): how many seconds.
        sample_rate (int): the sampling rate that relates time and samples.

    Returns:
        int: how many samples that `ms` equal.
    """
    return round(seconds * sample_rate)


def samples_to_ms(samples: int, sample_rate: int) -> float:
    """Compute how many milliseconds a number of samples equal.

    Args:
        samples (int): how many samples.
        sample_rate (int): the sampling rate that relates time and samples.

    Returns:
        float: the number of milliseconds that `samples` equal.
    """
    return 1000 * samples / sample_rate


def ms_to_samples(ms: float, sample_rate) -> int:
    """Compute how many samples a number of milliseconds equals.

    Args:
        ms (float): how many milliseconds.
        sample_rate (int): the sampling rate that relates time and samples.

    Returns:
        int: how many samples that `ms` equal.
    """
    return round(ms * sample_rate / 1000)


def lateral_fraction_early(bformat_rir: np.ndarray, sample_rate: int) -> float:
    """Compute the LF_early parameter.

    Args:
        bformat_rir (np.ndarray): a B-Format Ambisonics RIR, an array of shape (4, n)
            channels must be ordered as {W, X, Y, Z}.
        sample_rate (int): the sampling rate of the recording.

    Returns:
        float: the LF_early result in dB.
    """

    # Integration limits
    rir = bformat_rir[
        :, get_direct_sound_arrival(bformat_rir[0, :], sample_rate) :
    ].copy()
    samples_5ms = ms_to_samples(5, sample_rate)
    samples_80ms = ms_to_samples(80, sample_rate)

    # Integrate channel Y (lateral) between 5 and 80 ms
    lateral_portion = np.power(rir[2, samples_5ms:samples_80ms], 2).sum().squeeze()
    # Integrate channel W (omni) between 0 and 80 ms
    omni_portion = np.power(rir[0, 0:samples_80ms], 2).sum().squeeze()
    if np.isclose(omni_portion, 0.0, 1e-7):
        raise ValueError("Omni portion {} is too close to 0.0".format(omni_portion))

    ratio = lateral_portion / omni_portion
    if np.isclose(ratio, 0.0, 1e-7):
        return -np.inf
    return 10 * np.log10(ratio)


def lateral_fraction_late(bformat_rir: np.ndarray, sample_rate: int) -> float:
    """Compute the LF_late parameter.

    Args:
        bformat_rir (np.ndarray): a B-Format Ambisonics RIR, an array of shape (4, n)
            channels must be ordered as {W, X, Y, Z}.
        sample_rate (int): the sampling rate of the recording.

    Returns:
        float: the LF_late result in dB.
    """

    # Integration limits
    rir = bformat_rir.copy()[
        :, get_direct_sound_arrival(bformat_rir[0, :], sample_rate) :
    ]
    samples_80ms = ms_to_samples(80, sample_rate)

    # Integrate channel Y (lateral) from 80 ms on
    lateral_portion = np.power(rir[2, samples_80ms:], 2).sum()
    # Integrate channel W (omni) from 0 ms on
    omni_portion = np.power(rir[0, :], 2).sum()
    if np.isclose(omni_portion, 0.0, 1e-7):
        raise ValueError("Omni portion {} is too close to 0.0".format(omni_portion))

    ratio = lateral_portion / omni_portion
    if np.isclose(ratio, 0.0, 1e-7):
        return -np.inf
    return 10 * np.log10(ratio)


def direct_reverberant_ratio(
    omni_rir: np.ndarray,
    sample_rate: int,
    limit_integration_to_seconds: Optional[float] = 2,
) -> float:
    """Compute the DR parameter (direct-to-reverberant ratio).

    Args:
        omni_rir (np.ndarray): an omnidirectional RIR, an array of shape (n,).
        sample_rate (int): the sampling rate of the recording.

    Returns:
        float: the DR result in dB.
    """

    # Integration limits
    signal = omni_rir.copy()[
        get_direct_sound_arrival(omni_rir, sample_rate) :
    ]  # Trim to direct sound
    samples_2ms = ms_to_samples(2, sample_rate)

    # Direct sound: integrate between 0 and 2 ms
    direct_portion = np.power(signal[:samples_2ms], 2).sum()
    # Reverberant sound: integrate from 2 ms on
    reverberant_portion = np.power(
        signal[samples_2ms:]
        if limit_integration_to_seconds is None
        else signal[
            samples_2ms : seconds_to_samples(limit_integration_to_seconds, sample_rate)
        ],
        2,
    ).sum()

    if np.isclose(reverberant_portion, 0.0, 1e-7):
        raise ValueError(
            "Reverberant portion {} is too close to 0.0".format(reverberant_portion)
        )

    ratio = direct_portion / reverberant_portion
    if np.isclose(ratio, 0.0, 1e-7):
        print(
            f"DR division is close to 0.0:\n\t- {ratio = }\n\t- direct: {direct_portion}\n\t- reverberant {reverberant_portion}"
        )
        return -np.inf
    return 10 * np.log10(ratio)


def get_direct_sound_arrival(
    rir: np.ndarray, sample_rate: int, as_milliseconds: bool = False
) -> Union[float, int]:
    direct_sound_index = max(0, find_peaks(rir)[0][0] - ms_to_samples(1, sample_rate))
    return (
        samples_to_ms(get_direct_sound_arrival(rir, sample_rate), sample_rate)
        if as_milliseconds
        else direct_sound_index
    )


if __name__ == "__main__":
    aformat_rirs, sample_rate = read_aformat(
        [
            # 1. front left up
            # 2. front right down
            # 3. back left down
            # 4. back right up
            "./test/mock_data/regio_theater/soundfield_flu.wav",
            "./test/mock_data/regio_theater/soundfield_frd.wav",
            "./test/mock_data/regio_theater/soundfield_bld.wav",
            "./test/mock_data/regio_theater/soundfield_bru.wav",
        ]
    )
    bformat_rirs = convert_ambisonics_a_to_b(*[aformat_rirs[i, :] for i in range(4)])

    lf_early = lateral_fraction_early(bformat_rirs, sample_rate)
    lf_late = lateral_fraction_late(bformat_rirs, sample_rate)
    dr_ratio = direct_reverberant_ratio(bformat_rirs[0, :], sample_rate)
    print(
        f"LF_early = {lf_early:4.2f} dB\n\tLF_late = {lf_late:4.2f} dB\n\tDR = {dr_ratio:4.2f} dB"
    )
