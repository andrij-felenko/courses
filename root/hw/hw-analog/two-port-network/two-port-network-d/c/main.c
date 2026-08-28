// Перемноження двох ABCD-матриць (ланки поспіль).
// Матриця подана як {A, B, C, D}. Послідовний опір Z -> {1, Z, 0, 1}.
typedef struct { float A, B, C, D; } ABCD;

ABCD abcd_mul(ABCD m1, ABCD m2) {   // m1 — перша ланка, m2 — друга
    ABCD r;
    r.A = m1.A*m2.A + m1.B*m2.C;
    r.B = m1.A*m2.B + m1.B*m2.D;
    r.C = m1.C*m2.A + m1.D*m2.C;
    r.D = m1.C*m2.B + m1.D*m2.D;
    return r;
}

// Дві ланки з послідовним опором по 50 Ом:
// ABCD s1 = {1, 50, 0, 1};  ABCD s2 = {1, 50, 0, 1};
// abcd_mul(s1, s2) -> {1, 100, 0, 1}  ->  B = 100 Ом, тобто опори склалися
