#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

/* Комплексне число та операції над ним */
typedef struct {
    double real;
    double imag;
} DoubleComplex;

DoubleComplex c_make(double r, double i) {
    DoubleComplex z = {r, i};
    return z;
}

DoubleComplex c_add(DoubleComplex a, DoubleComplex b) {
    return c_make(a.real + b.real, a.imag + b.imag);
}

DoubleComplex c_mul(DoubleComplex a, DoubleComplex b) {
    return c_make(a.real * b.real - a.imag * b.imag,
                  a.real * b.imag + a.imag * b.real);
}

DoubleComplex c_conj(DoubleComplex a) {
    return c_make(a.real, -a.imag);
}

double c_abs_sq(DoubleComplex a) {
    return a.real * a.real + a.imag * a.imag;
}

/* Вектор Джонса 2x1 */
typedef struct {
    DoubleComplex ex;
    DoubleComplex ey;
} JonesVector;

/* Матриця Джонса 2x2 */
typedef struct {
    DoubleComplex m[2][2];
} JonesMatrix;

/* Вектор Стокса 4x1 */
typedef struct {
    double s0;
    double s1;
    double s2;
    double s3;
} StokesVector;

/* Множення матриці Джонса на вектор Джонса: J_out = M * J_in */
JonesVector jones_apply(JonesMatrix M, JonesVector J) {
    JonesVector res;
    res.ex = c_add(c_mul(M.m[0][0], J.ex), c_mul(M.m[0][1], J.ey));
    res.ey = c_add(c_mul(M.m[1][0], J.ex), c_mul(M.m[1][1], J.ey));
    return res;
}

/* Множення двох матриць Джонса: M_out = A * B */
JonesMatrix jones_mul_matrix(JonesMatrix A, JonesMatrix B) {
    JonesMatrix R;
    for (int i = 0; i < 2; i++) {
        for (int j = 0; j < 2; j++) {
            R.m[i][j] = c_make(0.0, 0.0);
            for (int k = 0; k < 2; k++) {
                R.m[i][j] = c_add(R.m[i][j], c_mul(A.m[i][k], B.m[k][j]));
            }
        }
    }
    return R;
}

/* Створення матриці фазової платівки під кутом theta (рад) із запізненням delta (рад) */
JonesMatrix make_retarder(double theta_rad, double delta_rad) {
    double c = cos(theta_rad);
    double s = sin(theta_rad);
    DoubleComplex phase = c_make(cos(delta_rad), sin(delta_rad));

    /* Базова матриця в власній системі координат */
    JonesMatrix J0;
    J0.m[0][0] = c_make(1.0, 0.0);
    J0.m[0][1] = c_make(0.0, 0.0);
    J0.m[1][0] = c_make(0.0, 0.0);
    J0.m[1][1] = phase;

    /* Матриця повороту R(theta) */
    JonesMatrix R, R_inv;
    R.m[0][0] = c_make(c, 0.0);  R.m[0][1] = c_make(s, 0.0);
    R.m[1][0] = c_make(-s, 0.0); R.m[1][1] = c_make(c, 0.0);

    R_inv.m[0][0] = c_make(c, 0.0); R_inv.m[0][1] = c_make(-s, 0.0);
    R_inv.m[1][0] = c_make(s, 0.0); R_inv.m[1][1] = c_make(c, 0.0);

    /* J = R(-theta) * J0 * R(theta) */
    JonesMatrix tmp = jones_mul_matrix(J0, R);
    return jones_mul_matrix(R_inv, tmp);
}

/* Створення матриці лінійного поляризатора під кутом theta (рад) */
JonesMatrix make_polarizer(double theta_rad) {
    double c = cos(theta_rad);
    double s = sin(theta_rad);

    JonesMatrix J;
    J.m[0][0] = c_make(c * c, 0.0);
    J.m[0][1] = c_make(c * s, 0.0);
    J.m[1][0] = c_make(c * s, 0.0);
    J.m[1][1] = c_make(s * s, 0.0);
    return J;
}

/* Перетворення вектора Джонса у вектор Стокса */
StokesVector jones_to_stokes(JonesVector J) {
    StokesVector S;
    double I_x = c_abs_sq(J.ex);
    double I_y = c_abs_sq(J.ey);

    DoubleComplex ex_ey_conj = c_mul(J.ex, c_conj(J.ey));

    S.s0 = I_x + I_y;
    S.s1 = I_x - I_y;
    S.s2 = 2.0 * ex_ey_conj.real;
    S.s3 = -2.0 * ex_ey_conj.imag;
    return S;
}

/* Обчислення ступеня поляризації (DOP) */
double stokes_dop(StokesVector S) {
    if (S.s0 <= 1e-15) return 0.0;
    double pol_int = sqrt(S.s1 * S.s1 + S.s2 * S.s2 + S.s3 * S.s3);
    return pol_int / S.s0;
}

int main(void) {
    /* Початковий стан: Горизонтально поляризоване світло J_in = (1, 0)^T */
    JonesVector J_in;
    J_in.ex = c_make(1.0, 0.0);
    J_in.ey = c_make(0.0, 0.0);

    printf("=== Симулятор поляризаційного тракту (C) ===\n");
    printf("Початковий стан (H-поляризація):\n");
    printf("Ex = %.3f + %.3fi, Ey = %.3f + %.3fi\n",
           J_in.ex.real, J_in.ex.imag, J_in.ey.real, J_in.ey.imag);

    /* 1. Чвертьхвильова платівка (QWP) під кутом 45° (delta = pi/2) */
    JonesMatrix QWP45 = make_retarder(45.0 * M_PI / 180.0, M_PI / 2.0);

    /* 2. Лінійний аналізатор під кутом 90° (вертикальний) */
    JonesMatrix Pol90 = make_polarizer(90.0 * M_PI / 180.0);

    /* Обчислення каскаду: J_mid = QWP45 * J_in */
    JonesVector J_mid = jones_apply(QWP45, J_in);
    StokesVector S_mid = jones_to_stokes(J_mid);

    printf("\nПісля чвертьхвильової платівки (+45°):\n");
    printf("Ex = %.3f + %.3fi, Ey = %.3f + %.3fi\n",
           J_mid.ex.real, J_mid.ex.imag, J_mid.ey.real, J_mid.ey.imag);
    printf("Вектор Стокса: S0=%.3f, S1=%.3f, S2=%.3f, S3=%.3f\n",
           S_mid.s0, S_mid.s1, S_mid.s2, S_mid.s3);
    printf("Ступінь поляризації (DOP): %.4f\n", stokes_dop(S_mid));

    /* J_out = Pol90 * J_mid */
    JonesVector J_out = jones_apply(Pol90, J_mid);
    StokesVector S_out = jones_to_stokes(J_out);

    printf("\nПісля аналізатора (90°):\n");
    printf("Вихідна інтенсивність (S0): %.4f (50%% від початкової)\n", S_out.s0);
    printf("Вектор Стокса: S0=%.3f, S1=%.3f, S2=%.3f, S3=%.3f\n",
           S_out.s0, S_out.s1, S_out.s2, S_out.s3);

    return 0;
}
