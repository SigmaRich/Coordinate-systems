import numpy as np
from transforms import convert, geodetic_to_ecef


def numeric_jacobian_pos(func, coord, eps=1e-6):

    coord = np.array(coord, dtype=float)
    f0 = np.array(func(coord))
    M = np.zeros((3, 3))
    for j in range(3):
        dp = coord.copy()
        dp[j] += eps
        M[:, j] = (np.array(func(dp)) - f0) / eps
    return M

def numeric_jacobian6(func, coord6, eps=1e-6):

    coord6 = np.array(coord6, dtype=float)
    f0 = np.array(func(coord6))
    n = coord6.size
    M6 = np.zeros((n, n))
    for j in range(n):
        dp = coord6.copy()
        dp[j] += eps
        M6[:, j] = (np.array(func(dp)) - f0) / eps
    return M6

def convert6(coord6, src, dst, station_params=None):

    if station_params and 'geo' in station_params:
        φ, λ, h = station_params['geo']
        off = np.array(geodetic_to_ecef(φ, λ, h), dtype=float)
        A = station_params.get('A', 0.0)
        b0 = station_params.get('beta0', 0.0)
    else:
        off = np.zeros(3)
        A = station_params.get('A', 0.0) if station_params else 0.0
        b0 = station_params.get('beta0', 0.0) if station_params else 0.0

    pos_raw = np.array(coord6[:3], dtype=float)
    vel_in  = np.array(coord6[3:], dtype=float)

    pos_in = pos_raw - off if src == "МПСК" else pos_raw

    pos_out = np.array(convert(tuple(pos_in), src, dst, A, b0))

    Jpos = numeric_jacobian_pos(lambda p: convert(tuple(p), src, dst, A, b0), pos_in)
    vel_out = Jpos.dot(vel_in)

    if dst == "МПСК":
        pos_out += off

    return np.hstack((pos_out, vel_out))

def propagate_uncertainty(coord6, src, dst, station_params, sigma_in, eps=1e-6):

    M6 = numeric_jacobian6(lambda c: convert6(c, src, dst, station_params), coord6, eps)

    K_in = np.diag(np.array(sigma_in, dtype=float)**2)

    K_out = M6.dot(K_in).dot(M6.T)

    sigma_out = np.sqrt(np.diag(K_out))
    return sigma_out
