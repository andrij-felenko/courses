#include <cmath>

// Закон Пелгрома: σ(ΔVth) = A_VT / sqrt(W·L).
// Усе в узгоджених одиницях: A_VT у В·мкм, W,L у мкм → σ у вольтах.
float sigma_vth(float a_vt_V_um, float W_um, float L_um) {
    return a_vt_V_um / std::sqrt(W_um * L_um);   // стандартне відхилення розкиду порогів пари
}

// Дзеркало струмів: відносна похибка копії ≈ (gm/ID)·σ(ΔVth).
float mirror_current_error(float a_vt, float W, float L, float gm_over_id) {
    return gm_over_id * sigma_vth(a_vt, W, L);   // частка (1.0 = 100 %)
}

// Диференційна пара: вхідний зсув нуля ≈ σ(ΔVth) самої пари.
float input_offset_V(float a_vt, float W, float L) {
    return sigma_vth(a_vt, W, L);                 // у вольтах
}

// Скільки разів збільшити ПЛОЩУ, щоб поліпшити узгодження у factor разів.
// Корінь у законі → площа росте як КВАДРАТ бажаного виграшу.
float area_growth_for(float factor) {
    return factor * factor;                       // хочеш удвічі краще — учетверо більша деталь
}

// Приклад прикидки для типового процесу.
void estimate() {
    constexpr float A_VT = 0.004f;   // 4 мВ·мкм — типовий коефіцієнт КМОН
    constexpr float W = 4.0f, L = 4.0f; // пара 4×4 мкм → площа 16 мкм²
    constexpr float gm_id = 15.0f;   // крутість на струм, типово 10…20 В⁻¹

    const float s_vth  = sigma_vth(A_VT, W, L);                 // ≈ 0.001 В = 1 мВ
    const float i_err  = mirror_current_error(A_VT, W, L, gm_id); // ≈ 0.015 = 1.5 %
    const float v_os   = input_offset_V(A_VT, W, L);           // ≈ 0.001 В = 1 мВ зсуву
    const float grow4x = area_growth_for(2.0f);                // = 4: удвічі краще = ×4 площі
    (void)s_vth; (void)i_err; (void)v_os; (void)grow4x;
}
