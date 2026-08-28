// Цифровий двійник RC-інтегратора (дірявого): експоненційне згладжування.
// V_out += (dt/τ) · (V_in − V_out)  — рівно те, що робить конденсатор за крок dt.
#include <stdint.h>

static float v_out = 0.0f;          // «напруга на конденсаторі» — згладжений вихід

float rc_integrate(float v_in) {
    const float dt    = 0.1e-3f;    // крок опитування, 0.1 мс
    const float tau   = 5.0e-3f;    // стала часу RC, 5 мс
    const float alpha = dt / tau;   // частка нового струму за крок ≈ 0.02
    v_out += alpha * (v_in - v_out);
    return v_out;
}
