import math


def distance(x1: float, y1: float, x2: float, y2: float) -> float:
    """Calculate the Euclidean distance between the two points.

    Parameters
    ----------
    x1 : float
        The x-coordinate of the first point.
    y1 : float
        The y-coordinate of the first point.
    x2 : float
        The x-coordinate of the second point.
    y2 : float
        The y-coordinate of the second point.

    Returns
    -------
    float
        The Euclidean distance between the two points.
    """    
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def free_space_path_loss(dist: float, frequency_mhz: float) -> float:
    """Free-space path loss in dB.
    Formula: FSPL(dB) = 20*log10(d) + 20*log10(f) + 32.44
    where d is in km and f is in MHz.

    Parameters
    ----------
    dist : float
        The distance between the two points (m).
    frequency_mhz : float
        The frequency of the signal (MHz).

    Returns
    -------
    float
        The free-space path loss in dB.
    """    
    if dist <= 0:
        return 0.0
    dist_km = dist / 1000.0
    return 20 * math.log10(dist_km) + 20 * math.log10(frequency_mhz) + 32.44


def received_power(transmit_power_dbm: float, path_loss_db: float) -> float:
    """Recevied signal in dBm

    Parameters
    ----------
    transmit_power_dbm : float
        The transmit power in dBm.
    path_loss_db : float
        The path loss in dB.

    Returns
    -------
    float
        The received signal power in dBm.
    """    
    return transmit_power_dbm - path_loss_db
