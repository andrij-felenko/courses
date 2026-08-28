function abcd(A, B, C, D) { return { A, B, C, D }; }

function abcdMul(m1, m2) {     // m1 — перша за сигналом ланка
    return {
        A: m1.A * m2.A + m1.B * m2.C,
        B: m1.A * m2.B + m1.B * m2.D,
        C: m1.C * m2.A + m1.D * m2.C,
        D: m1.C * m2.B + m1.D * m2.D,
    };
}

// Цеглинки з бібліотеки:
const seriesZ = (Z) => abcd(1.0, Z,   0.0, 1.0);   // {1,Z,0,1}
const shuntY  = (Y) => abcd(1.0, 0.0, Y,   1.0);   // {1,0,Y,1}

// Перевірка взаємності: для пасивної ланки має бути AD − BC ≈ 1.
const reciprocity = (m) => m.A * m.D - m.B * m.C;
