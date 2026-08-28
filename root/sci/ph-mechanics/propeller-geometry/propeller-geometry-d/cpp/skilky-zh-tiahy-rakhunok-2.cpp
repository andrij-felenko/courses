#include <cmath>

// Кут установки перерізу лопаті на радіусі r за геометричним кроком P.
// tan(beta) = P / (2·π·r)  →  beta = atan( P / (2·π·r) )
float blade_angle_deg(float pitch_m, float r_m) {
    float beta = std::atan(pitch_m / (2.0f * 3.14159265f * r_m));
    return beta * 180.0f / 3.14159265f;
}

int main() {
    float r75 = 0.75f * 0.064f;                 // 0.048 м — переріз 75 % радіуса
    float beta = blade_angle_deg(0.114f, r75);
    // tan β = 0.114 / (2·π·0.048) = 0.114 / 0.3016 = 0.378
    // β = atan(0.378) ≈ 20.7°
    return 0;
}
