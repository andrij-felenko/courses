#include <math.h>

// Уся кількісна фізика координованого розвороту з одного кута й швидкості.
typedef struct {
    float load_factor;   // n = 1/cos φ  (у скільки разів важче)
    float radius_m;      // r = V²/(g·tan φ)  радіус дуги, м
    float rate_deg_s;    // ω = g·tan φ / V   кутова швидкість, °/с
    float stall_mult;    // √n  у скільки разів вища швидкість зриву
} turn_t;

turn_t turn_geometry(float V_ms, float bank_deg) {
    const float g   = 9.81f;
    float phi = bank_deg * (float)M_PI / 180.0f;   // градуси → радіани
    float c = cosf(phi), t = tanf(phi);

    turn_t o;
    o.load_factor = 1.0f / c;                       // n = 1/cos φ
    o.radius_m    = (V_ms * V_ms) / (g * t);        // r = V²/(g·tan φ)
    o.rate_deg_s  = (g * t / V_ms) * 180.0f / (float)M_PI;  // ω, назад у °/с
    o.stall_mult  = sqrtf(o.load_factor);           // √n
    return o;
}
