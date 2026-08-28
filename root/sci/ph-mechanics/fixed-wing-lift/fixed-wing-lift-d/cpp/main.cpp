#include <math.h>

// Швидкість, за якої підіймальна сила зрівноважує вагу.
// L = 0.5*rho*v^2*S*CL = m*g   ->   v = sqrt( 2*m*g / (rho*S*CL) )
float level_flight_speed(float m, float S, float CL, float rho) {
    const float g = 9.81f;
    return sqrtf(2.0f * m * g / (rho * S * CL));
}

// виклик: level_flight_speed(2.0f, 0.30f, 0.6f, 1.225f);
