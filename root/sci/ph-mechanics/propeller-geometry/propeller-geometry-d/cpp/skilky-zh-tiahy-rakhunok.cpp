#include <cmath>

// Ідеальна статична тяга гвинта за теорією імпульсу (висіння, V0 = 0).
// P_shaft — механічна потужність на валу (Вт), R — радіус гвинта (м).
float hover_thrust(float P_shaft, float R, float rho) {
    float A = 3.14159265f * R * R;          // заметена площа, м^2
    // T = (2 * rho * A * P^2)^(1/3)
    return std::cbrt(2.0f * rho * A * P_shaft * P_shaft);
}

int main() {
    float T = hover_thrust(180.0f, 0.125f, 1.2f);
    // A = π·0.125² = 0.0491 м²
    // T = (2 · 1.2 · 0.0491 · 180²)^(1/3)
    //   = (2 · 1.2 · 0.0491 · 32400)^(1/3)
    //   = (3817)^(1/3) ≈ 15.6 Н
    return 0;
}
