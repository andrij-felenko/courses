import math

# Радіус Землі — середній (IUGG), метри. Він мінімізує середньоквадратичну
# похибку дуги проти реального геоїда; для навігації цієї точності з надлишком.
EARTH_RADIUS_M = 6371000.0

# haversin(x) = sin²(x/2). Виносимо окремо — так формула читається один-в-один.
def haversin(x_rad):
    s = math.sin(x_rad * 0.5)
    return s * s

# Відстань по поверхні (метри) між (lat1,lon1) і (lat2,lon2) за гаверсинусами.
def great_circle_m(lat1, lon1, lat2, lon2):
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)   # Δφ
    dlam = math.radians(lon2 - lon1)   # Δλ

    # a = sin²(Δφ/2) + cosφ₁·cosφ₂·sin²(Δλ/2)  — гаверсинус центрального кута.
    a = haversin(dphi) + math.cos(phi1) * math.cos(phi2) * haversin(dlam)

    # c = 2·atan2(√a, √(1−a)) — сам кут θ, стійко на всьому діапазоні.
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))

    return EARTH_RADIUS_M * c            # d = R·θ
