import math

# WGS84 — еліпсоїд, на якому GNSS міряє координати
A  = 6378137.0                 # велика піввісь, м
F  = 1.0 / 298.257223563       # стиснення
E2 = F * (2.0 - F)             # квадрат першого ексцентриситету

def geodetic_to_ecef(lat_deg, lon_deg, h):
    """Географічні (широта, довгота у °, висота в м) → ECEF (X, Y, Z), м."""
    lat, lon = math.radians(lat_deg), math.radians(lon_deg)
    sf, cf = math.sin(lat), math.cos(lat)
    sl, cl = math.sin(lon), math.cos(lon)
    N = A / math.sqrt(1.0 - E2 * sf * sf)          # радіус кривини першого вертикала
    x = (N + h) * cf * cl
    y = (N + h) * cf * sl
    z = (N * (1.0 - E2) + h) * sf
    return x, y, z

def ecef_to_enu(p, ref, lat0_deg, lon0_deg):
    """ECEF-точку → місцеві East-North-Up відносно опори (lat0, lon0 та її ECEF ref)."""
    dx, dy, dz = p[0] - ref[0], p[1] - ref[1], p[2] - ref[2]   # трансляція: відняли опору
    sf, cf = math.sin(math.radians(lat0_deg)), math.cos(math.radians(lat0_deg))
    sl, cl = math.sin(math.radians(lon0_deg)), math.cos(math.radians(lon0_deg))
    east  =        -sl*dx +        cl*dy                        # поворот на місцеві осі
    north = -sf*cl*dx - sf*sl*dy + cf*dz
    up    =  cf*cl*dx + cf*sl*dy + sf*dz
    return east, north, up

# опорна точка — нуль місцевої сітки (злітний майданчик)
ref = geodetic_to_ecef(50.4500, 30.5200, 180.0)
# дрон, як його бачить GNSS
drone = geodetic_to_ecef(50.4510, 30.5225, 205.0)

e, n, u = ecef_to_enu(drone, ref, 50.4500, 30.5200)
print(f"E={e:.2f}  N={n:.2f}  U={u:.2f} м")
# E=177.56  N=111.24  U=25.00 м
