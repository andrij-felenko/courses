from math import sqrt

# Повітряна швидкість із перепаду тиску Пито (гальмівний − статичний).
# v = sqrt( 2*dp / rho )
def airspeed_from_dp(dp_pa, rho):
    if dp_pa <= 0.0:
        return 0.0
    return sqrt(2.0 * dp_pa / rho)

# виклик: airspeed_from_dp(200.0, 1.225)
