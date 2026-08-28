import math

# Означальні сталі WGS-84 (задані точно, не виміряні).
WGS84_A     = 6_378_137.0          # велика піввісь, м
WGS84_INV_F = 298.257223563        # обернене сплющення

def wgs84_radii(lat_deg: float) -> tuple[float, float]:
    """Меридіанний радіус M і радіус першого вертикала N на заданій широті."""
    f  = 1.0 / WGS84_INV_F
    e2 = 2.0 * f - f * f                      # квадрат ексцентриситету
    s  = math.sin(math.radians(lat_deg))
    w2 = 1.0 - e2 * s * s
    w  = math.sqrt(w2)
    return WGS84_A * (1.0 - e2) / (w2 * w), WGS84_A / w

def metres_per_degree(lat_deg: float) -> tuple[float, float]:
    """Скільки метрів в одному градусі широти й довготи на цій широті."""
    m, n = wgs84_radii(lat_deg)
    rad = math.radians(1.0)
    return m * rad, n * rad * math.cos(math.radians(lat_deg))

# metres_per_degree(50.0) -> (111229.0..., 71696.0...)
