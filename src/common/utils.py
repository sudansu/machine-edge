import numpy as np

def get_source_change_rate(src):
    rate = np.empty(len(src))
    rate[0] = 1.0
    for i in range(1, len(rate)):
        rate[i] = src[i] / src[i-1]
    return rate

def get_source_norm(src):
    norm = np.empty(len(src))
    min_v = min(src)
    max_v = max(src)
    for i in range(len(norm)):
        norm[i] = (src[i] - min_v) / (max_v - min_v)
    return norm
