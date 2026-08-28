import math

MU_WATER = 1.0e-3   # Па·с — в'язкість води при ~20 °C

def pipe_resistance(radius, length, mu):
    """Гідравлічний опір круглої труби за Пуазейлем, [Па·с/м³].
    radius, length — у метрах; mu — у Па·с. Уся сила — у radius**4."""
    return 8.0 * mu * length / (math.pi * radius**4)

def flow(dp, R):
    """Витрата крізь опір R під натиском dp:  Q = dp / R, [м³/с]."""
    return dp / R
