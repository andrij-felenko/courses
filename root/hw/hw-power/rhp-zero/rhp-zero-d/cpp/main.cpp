#include <numbers>

// Частота RHP-нуля бусту в CCM та безпечна стеля смуги контуру.
// Vin, Vout — вольти; Iout — ампери; L — генрі.
float rhpz_boost_hz(float Vin, float Vout, float Iout, float L) {
    float D = 1.0f - Vin / Vout;           // шпаруватість
    float R = Vout / Iout;                 // опір навантаження
    float k = (1.0f - D) * (1.0f - D);     // (1 − D)²
    return R * k / (2.0f * std::numbers::pi_v<float> * L);
}

// Смугу контуру безпечно тримати ~у 4 рази нижче за нуль.
float loop_bw_limit_hz(float f_rhpz) {
    return f_rhpz / 4.0f;
}

// приклад: 5 В → 12 В, 1 А, 22 мкГн
// f_rhpz ≈ 15.1 кГц  →  стеля смуги ≈ 3.8 кГц
