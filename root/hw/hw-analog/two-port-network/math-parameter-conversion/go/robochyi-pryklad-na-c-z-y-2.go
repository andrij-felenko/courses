package twoport

type ABCD struct{ A, B, C, D float64 }

func abcdMul(m1, m2 ABCD) ABCD {     // m1 — перша за сигналом ланка
    return ABCD{
        A: m1.A*m2.A + m1.B*m2.C,
        B: m1.A*m2.B + m1.B*m2.D,
        C: m1.C*m2.A + m1.D*m2.C,
        D: m1.C*m2.B + m1.D*m2.D,
    }
}

// Цеглинки з бібліотеки:
func seriesZ(Z float64) ABCD { return ABCD{1.0, Z, 0.0, 1.0} }  // {1,Z,0,1}
func shuntY(Y float64) ABCD  { return ABCD{1.0, 0.0, Y, 1.0} }  // {1,0,Y,1}

// Перевірка взаємності: для пасивної ланки має бути AD − BC ≈ 1.
func reciprocity(m ABCD) float64 { return m.A*m.D - m.B*m.C }
