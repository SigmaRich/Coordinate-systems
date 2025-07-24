import numpy as np

def geodetic_to_ecef(phi_deg, lam_deg, h, R=6371000.0):

    φ = np.deg2rad(phi_deg)
    λ = np.deg2rad(lam_deg)
    r = R + h
    x = r * np.cos(φ) * np.cos(λ)
    y = r * np.cos(φ) * np.sin(λ)
    z = r * np.sin(φ)
    return (x, y, z)

# Сферические ↔ Декартовы
def spherical_to_cartesian(R, alpha, beta):
    x = R * np.cos(beta) * np.sin(alpha)
    y = R * np.cos(beta) * np.cos(alpha)
    z = R * np.sin(beta)
    return np.array([x, y, z])

def cartesian_to_spherical(x, y, z):
    R = np.sqrt(x**2 + y**2 + z**2)
    beta = np.arcsin(z / R)
    alpha = np.arctan2(x, y)
    return R, alpha, beta

# Повороты вокруг осей
def rotate_about_z(v, angle):
    c, s = np.cos(angle), np.sin(angle)
    Rz = np.array([[c, -s, 0],
                   [s,  c, 0],
                   [0,  0, 1]])
    return Rz.dot(v)

def rotate_about_x(v, angle):
    c, s = np.cos(angle), np.sin(angle)
    Rx = np.array([[1, 0,  0],
                   [0, c, -s],
                   [0, s,  c]])
    return Rx.dot(v)

# Универсальный конвертер (3D)
def convert(coord, src, dst, A=0.0, beta0=0.0):
    if src == "МПСК":
        v = rotate_about_z(np.array(coord), -A)
    elif src == "ССССК":
        v_tmp = spherical_to_cartesian(*coord)
        v = rotate_about_z(v_tmp, -A)
    elif src == "БСК":
        v_tmp = spherical_to_cartesian(*coord)
        v = rotate_about_x(v_tmp, -(np.pi/2 - beta0))
    elif src == "ССК":
        v_tmp = spherical_to_cartesian(*coord)
        v = rotate_about_z(v_tmp, A)
    else:
        raise ValueError(f"Unknown src: {src}")

    if dst == "МПСК":
        return tuple(rotate_about_z(v, A))
    elif dst == "ССССК":
        v2 = rotate_about_z(v, A)
        return cartesian_to_spherical(*v2)
    elif dst == "БСК":
        v2 = rotate_about_x(v, (np.pi/2 - beta0))
        return cartesian_to_spherical(*v2)
    elif dst == "ССК":
        v2 = rotate_about_z(v, -A)
        return cartesian_to_spherical(*v2)
    else:
        raise ValueError(f"Unknown dst: {dst}")
