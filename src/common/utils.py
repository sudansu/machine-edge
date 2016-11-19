import numpy as np

def get_source_change_rate(src):
    """
    Get change rate from a source list.

    Args:
        src: A list of float values

    Returns:
        A list of float values
    """
    rate = np.empty(len(src))
    rate[0] = 1.0
    for i in range(1, len(rate)):
        rate[i] = src[i] / src[i-1]
    return rate

def get_source_norm(src):
    """
    Get normalized values from a source list.

    Args:
        src: A list of float values

    Returns:
        A list of float values
    """
    norm = np.empty(len(src))
    min_v = min(src)
    max_v = max(src)
    for i in range(len(norm)):
        norm[i] = (src[i] - min_v) / (max_v - min_v)
    return norm
