def design_min_radius(g_frac, rpm_limit):
    """Найменша станція, що дає g_frac при обертах ≤ rpm_limit.
    Найменший радіус — на найбільших дозволених обертах: r = a/ω²."""
    a = g_frac * G_EARTH
    w = rpm_to_rad(rpm_limit)
    return Habitat(r=a / w**2, omega=w)


def at_radius(g_frac, r):
    """Станція радіусом r, розкручена так, щоб на ободі було саме g_frac."""
    w = math.sqrt(g_frac * G_EARTH / r)        # з ω²·r = a
    return Habitat(r=r, omega=w)
