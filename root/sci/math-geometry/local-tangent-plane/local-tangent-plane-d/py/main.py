import math
from dataclasses import dataclass

# Радіус Землі (середній сферичний). Точна реалізація бере широто-залежний
# радіус кривини сфероїда WGS84; для дрона різниця тоне в шумі GPS.
EARTH_R = 6_371_000.0                    # м
DEG2RAD = math.pi / 180.0

@dataclass
class Geo:                # градуси
    lat: float
    lon: float

@dataclass
class NE:                 # метри від точки-початку
    north: float
    east: float

# Перехід lat/lon -> місцеві метри «північ, схід» відносно origin.
def latlon_to_ne(origin: Geo, p: Geo) -> NE:
    dlat = (p.lat - origin.lat) * DEG2RAD   # приріст широти в радіанах
    dlon = (p.lon - origin.lon) * DEG2RAD   # приріст довготи в радіанах
    return NE(
        north=EARTH_R * dlat,                             # меридіан однаковий скрізь
        east=EARTH_R * dlon * math.cos(origin.lat * DEG2RAD),  # косинус — у origin
    )

# Приклад: маршрутна точка на 0.001 градуса північніше й східніше,
# origin на широті Києва (~50.45).
def demo() -> None:
    origin = Geo(50.4501, 30.5234)
    wp     = Geo(50.4511, 30.5244)   # +0.001° по кожній осі
    d = latlon_to_ne(origin, wp)
    # d.north ≈ 111.2 м  (0.001° широти)
    # d.east  ≈  71.0 м  (0.001° довготи · cos 50.45°)
