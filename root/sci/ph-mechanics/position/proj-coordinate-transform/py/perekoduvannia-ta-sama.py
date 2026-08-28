import math

def rect_to_polar(x, y):
    """Прямокутні (x, y) → полярні (r, φ). φ у радіанах, у діапазоні (−π, π]."""
    r   = math.hypot(x, y)      # √(x² + y²), стійке навіть до дуже великих чисел
    phi = math.atan2(y, x)      # НЕ atan(y/x): atan2 знає чверть
    return r, phi

def polar_to_rect(r, phi):
    """Полярні (r, φ) → прямокутні (x, y)."""
    return r * math.cos(phi), r * math.sin(phi)
