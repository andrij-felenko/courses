#include <cmath>

struct Zparams { float z11, z12, z21, z22; };
struct Yparams { float y11, y12, y21, y22; };

// Z -> Y оберненням матриці 2×2: Y = Z⁻¹.
// Повертає true при успіху, false якщо матриця вироджена (det ≈ 0, Y не існує).
bool z_to_y(Zparams z, Yparams &y) {
    float det = z.z11 * z.z22 - z.z12 * z.z21;   // ΔZ — визначник
    if (std::fabs(det) < 1e-12f) return false;    // вироджена: Y не існує
    y.y11 =  z.z22 / det;      // діагональ міняється місцями!
    y.y12 = -z.z12 / det;
    y.y21 = -z.z21 / det;
    y.y22 =  z.z11 / det;
    return true;
}
// Приклад: Z = {60, 40, 40, 80} Ом (взаємна, бо z12=z21).
//   det = 60·80 − 40·40 = 4800 − 1600 = 3200
//   y11 = 80/3200 = 0.025 См;  y22 = 60/3200 = 0.01875 См
//   y12 = y21 = −40/3200 = −0.0125 См   ← взаємність збереглася: Y₁₂ = Y₂₁
