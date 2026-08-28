package twoport

import "math"

type Zparams struct{ Z11, Z12, Z21, Z22 float64 }
type Yparams struct{ Y11, Y12, Y21, Y22 float64 }

// zToY: Z -> Y оберненням матриці 2×2: Y = Z⁻¹.
// Повертає (Y, true) при успіху, (нуль, false) якщо матриця вироджена.
func zToY(z Zparams) (Yparams, bool) {
    det := z.Z11*z.Z22 - z.Z12*z.Z21   // ΔZ — визначник
    if math.Abs(det) < 1e-12 {         // вироджена: Y не існує
        return Yparams{}, false
    }
    return Yparams{
        Y11:  z.Z22 / det,     // діагональ міняється місцями!
        Y12: -z.Z12 / det,
        Y21: -z.Z21 / det,
        Y22:  z.Z11 / det,
    }, true
}
// Приклад: Z = {60, 40, 40, 80} Ом (взаємна, бо z12=z21).
//   det = 60·80 − 40·40 = 4800 − 1600 = 3200
//   y11 = 80/3200 = 0.025 См;  y22 = 60/3200 = 0.01875 См
//   y12 = y21 = −40/3200 = −0.0125 См   ← взаємність збереглася: Y₁₂ = Y₂₁
