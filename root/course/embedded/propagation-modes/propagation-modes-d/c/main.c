#include <math.h>

// Дальність до радіообрію (км) для антени на висоті h (метрів).
float radio_horizon_km(float h_m) {
    return 3.57f * sqrtf(h_m);
}

float d_ground = radio_horizon_km(10.0f);    // станція на щоглі 10 м
float d_drone  = radio_horizon_km(100.0f);   // дрон на висоті 100 м
float d_max    = d_ground + d_drone;         // повний просвіт між ними
// d_ground ≈ 11.3 км
// d_drone  ≈ 35.7 км
// d_max    ≈ 47.0 км
