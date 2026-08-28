def ellipse_fit(x, y):
    """Підгонка a·x² + b·x·y + c·y² = 1 за МНК. Повертає (φ, A, B)."""
    x = x - x.mean()
    y = y - y.mean()
    M = np.column_stack([x * x, x * y, y * y])
    a, b, c = np.linalg.lstsq(M, np.ones(len(x)), rcond=None)[0]
    cos_phi = max(-1.0, min(1.0, -b / (2.0 * math.sqrt(a * c))))
    sin_phi = math.sqrt(max(1e-18, 1.0 - cos_phi * cos_phi))
    phi = math.copysign(math.acos(cos_phi), signed_area(x, y))
    return phi, 1.0 / (math.sqrt(a) * sin_phi), 1.0 / (math.sqrt(c) * sin_phi)
