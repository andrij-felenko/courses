import math

# WGS-84: перші дві сталі — точні за означенням, третя з них випливає.
WGS84_A = 6378137.0                    # велика піввісь, м
WGS84_F = 1.0 / 298.257223563          # сплюснутість
WGS84_E2 = WGS84_F * (2.0 - WGS84_F)   # квадрат ексцентриситету


def geodetic_to_ecef(lat_deg, lon_deg, h):
    """(φ, λ, h) -> ECEF; координати мають порядок 6.4·10⁶ м."""
    phi, lam = math.radians(lat_deg), math.radians(lon_deg)
    s, c = math.sin(phi), math.cos(phi)
    n = WGS84_A / math.sqrt(1.0 - WGS84_E2 * s * s)
    p = (n + h) * c                             # відстань до осі обертання
    return (p * math.cos(lam),
            p * math.sin(lam),
            (n * (1.0 - WGS84_E2) + h) * s)


def rotate_to_enu(v, lat_deg, lon_deg):
    """Поворот ВІЛЬНОГО вектора з ECEF у місцеву трійку — рядки матриці R_ENU."""
    phi, lam = math.radians(lat_deg), math.radians(lon_deg)
    sp, cp = math.sin(phi), math.cos(phi)
    sl, cl = math.sin(lam), math.cos(lam)
    x, y, z = v
    return (-sl * x + cl * y,
            -sp * cl * x - sp * sl * y + cp * z,
            cp * cl * x + cp * sl * y + sp * z)


def point_to_enu(origin, p):
    """ТОЧКА: спершу відняти початок, аж потім повертати — на кути ПОЧАТКУ."""
    x0, y0, z0 = geodetic_to_ecef(*origin)
    x, y, z = geodetic_to_ecef(*p)
    return rotate_to_enu((x - x0, y - y0, z - z0), origin[0], origin[1])


def enu_to_ned(q):
    """NED — та сама трійка в іншому порядку."""
    east, north, up = q
    return (north, east, -up)
