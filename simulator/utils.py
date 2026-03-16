"""Utility functions for RF propagation calculations."""

import math


def free_space_path_loss_db(distance_m: float, frequency_hz: float) -> float:
    """Return free-space path loss in dB between isotropic antennas.

    Uses the Friis formula:
        FSPL (dB) = 20·log10(4π·d·f / c)

    Args:
        distance_m: Separation distance in metres. Must be > 0.
        frequency_hz: Carrier frequency in Hz. Must be > 0.

    Returns:
        Path loss in dB (positive value means attenuation).

    Raises:
        ValueError: If distance_m or frequency_hz is not positive.
    """
    if distance_m <= 0:
        raise ValueError(f"distance_m must be positive, got {distance_m}")
    if frequency_hz <= 0:
        raise ValueError(f"frequency_hz must be positive, got {frequency_hz}")
    c = 3e8  # speed of light in m/s
    return 20 * math.log10(4 * math.pi * distance_m * frequency_hz / c)


def dbm_to_watts(dbm: float) -> float:
    """Convert power level from dBm to Watts.

    Args:
        dbm: Power in dBm.

    Returns:
        Power in Watts.
    """
    return 10 ** ((dbm - 30) / 10)


def watts_to_dbm(watts: float) -> float:
    """Convert power level from Watts to dBm.

    Args:
        watts: Power in Watts. Must be > 0.

    Returns:
        Power in dBm.

    Raises:
        ValueError: If watts is not positive.
    """
    if watts <= 0:
        raise ValueError(f"watts must be positive, got {watts}")
    return 10 * math.log10(watts) + 30
