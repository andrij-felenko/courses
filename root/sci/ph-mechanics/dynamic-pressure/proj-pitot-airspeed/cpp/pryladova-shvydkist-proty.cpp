#define R_AIR   287.05f      // Дж/(кг·К) — питома газова стала сухого повітря
#define RHO_SSL 1.225f       // кг/м³ — густина ISA на рівні моря
#define P_SSL   101325.0f    // Па — тиск ISA на рівні моря
#define GAMMA   1.4f         // показник адіабати повітря

float air_density(float p_static, float T_kelvin) {
    return p_static / (R_AIR * T_kelvin);         // ρ = p/(R·T)
}

float eas_from_dp(float dp) {                     // приладова (еталонна ρ₀)
    return (dp <= 0.0f) ? 0.0f : sqrtf(2.0f * dp / RHO_SSL);
}

float tas_from_dp(float dp, float rho) {          // справжня (реальна ρ)
    return (dp <= 0.0f) ? 0.0f : sqrtf(2.0f * dp / rho);
}
