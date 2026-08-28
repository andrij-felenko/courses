import math

WGS84_A = 6378137.0
WGS84_F = 1.0 / 298.257223563
WGS84_E2 = WGS84_F * (2.0 - WGS84_F)
WGS84_B = WGS84_A * (1.0 - WGS84_F)
WGS84_EP2 = WGS84_E2 / (1.0 - WGS84_E2)


def _height_from(p, z, phi):
    """Висоту беремо тією формулою, у якій знаменник не близький до нуля."""
    s, c = math.sin(phi), math.cos(phi)
    n = WGS84_A / math.sqrt(1.0 - WGS84_E2 * s * s)
    return p / c - n if abs(c) > 0.5 else z / s - n * (1.0 - WGS84_E2)


def ecef_to_geodetic(x, y, z, steps=1):
    """Боуринг 1976: один крок для всього наземного, другий — для орбіт."""
    p = math.hypot(x, y)

    # Усередині цього еліпса нормаль не єдина — широти просто немає.
    if p * p + (1.0 - WGS84_E2) * z * z < (WGS84_E2 * WGS84_A) ** 2:
        raise ValueError("точка всередині еволюти: розв'язок неоднозначний")

    beta = math.atan2(WGS84_A * z, WGS84_B * p)          # точно при h = 0
    phi = 0.0
    for _ in range(steps):
        sb, cb = math.sin(beta), math.cos(beta)
        phi = math.atan2(z + WGS84_EP2 * WGS84_B * sb ** 3,
                         p - WGS84_E2 * WGS84_A * cb ** 3)
        beta = math.atan2((1.0 - WGS84_F) * math.sin(phi), math.cos(phi))

    return (math.degrees(phi), math.degrees(math.atan2(y, x)),
            _height_from(p, z, phi))


def ecef_to_geodetic_iter(x, y, z):
    """Проста ітерація: |F'| <= e² = 0.0067, тож п'ять кроків вистачає завжди."""
    p = math.hypot(x, y)
    phi = math.atan2(z, p * (1.0 - WGS84_E2))            # старт: h = 0
    for _ in range(5):
        s = math.sin(phi)
        n = WGS84_A / math.sqrt(1.0 - WGS84_E2 * s * s)
        phi = math.atan2(z + WGS84_E2 * n * s, p)
    return (math.degrees(phi), math.degrees(math.atan2(y, x)),
            _height_from(p, z, phi))
