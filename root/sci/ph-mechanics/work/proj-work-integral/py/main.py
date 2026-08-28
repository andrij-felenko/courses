import numpy as np

def cycle_energy(F, v, dt):
    """Енергія за цикл із логу сили й швидкості, рівний крок dt (с)."""
    return float(np.sum(F * v) * dt)          # Σ F·v·Δt — знак і все

# нерівний такт: беремо справжні мітки часу t і трапецію по потужності
def cycle_energy_uneven(F, v, t):
    P = F * v                                  # миттєва потужність
    return float(np.sum(0.5 * (P[:-1] + P[1:]) * np.diff(t)))
