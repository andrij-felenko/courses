#include <math.h>

// Повітряна швидкість із перепаду тиску Пито (гальмівний − статичний).
// v = sqrt( 2*dp / rho )
float airspeed_from_dp(float dp_pa, float rho) {
    if (dp_pa <= 0.0f) return 0.0f;   // від'ємний перепад — шум або зустрічний бік
    return sqrtf(2.0f * dp_pa / rho);
}

// виклик: airspeed_from_dp(200.0f, 1.225f);
