struct ABCD { float A, B, C, D; };

ABCD abcd_mul(ABCD m1, ABCD m2) {     // m1 — перша за сигналом ланка
    ABCD r;
    r.A = m1.A * m2.A + m1.B * m2.C;
    r.B = m1.A * m2.B + m1.B * m2.D;
    r.C = m1.C * m2.A + m1.D * m2.C;
    r.D = m1.C * m2.B + m1.D * m2.D;
    return r;
}

// Цеглинки з бібліотеки:
ABCD series_z(float Z) { return {1.0f, Z,    0.0f, 1.0f}; }  // {1,Z,0,1}
ABCD shunt_y(float Y)  { return {1.0f, 0.0f, Y,    1.0f}; }  // {1,0,Y,1}

// Перевірка взаємності: для пасивної ланки має бути AD − BC ≈ 1.
float reciprocity(ABCD m) { return m.A * m.D - m.B * m.C; }
