#include <stdio.h>
#include <math.h>
#include <stdbool.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

/* Комплексне число та базові операції */
typedef struct {
    double real;
    double imag;
} Complex;

static inline Complex complex_create(double r, double i) {
    Complex c = {r, i};
    return c;
}

static inline Complex complex_add(Complex a, Complex b) {
    return complex_create(a.real + b.real, a.imag + b.imag);
}

static inline Complex complex_sub(Complex a, Complex b) {
    return complex_create(a.real - b.real, a.imag - b.imag);
}

static inline Complex complex_mul(Complex a, Complex b) {
    return complex_create(a.real * b.real - a.imag * b.imag,
                          a.real * b.imag + a.imag * b.real);
}

static inline double complex_abs_sq(Complex c) {
    return c.real * c.real + c.imag * c.imag;
}

/* Вектор Джонса (2x1) */
typedef struct {
    Complex ex;
    Complex ey;
} JonesVector;

/* Матриця Джонса (2x2) */
typedef struct {
    Complex m00, m01;
    Complex m10, m11;
} JonesMatrix;

/* Створення лінійно поляризованого вектора під кутом theta (рад) */
JonesVector jones_vector_linear(double amplitude, double theta_rad) {
    JonesVector v;
    v.ex = complex_create(amplitude * cos(theta_rad), 0.0);
    v.ey = complex_create(amplitude * sin(theta_rad), 0.0);
    return v;
}

/* Створення кругово поляризованого вектора (право- або лівообертального) */
JonesVector jones_vector_circular(double amplitude, bool right_handed) {
    JonesVector v;
    double norm_amp = amplitude / sqrt(2.0);
    v.ex = complex_create(norm_amp, 0.0);
    /* Right-handed: phase shift +pi/2 (i), Left-handed: -pi/2 (-i) */
    v.ey = complex_create(0.0, right_handed ? norm_amp : -norm_amp);
    return v;
}

/* Обчислення інтенсивності світла */
double jones_intensity(JonesVector v) {
    return complex_abs_sq(v.ex) + complex_abs_sq(v.ey);
}

/* Множення матриці Джонса 2x2 на вектор Джонса 2x1 */
JonesVector jones_apply(JonesMatrix M, JonesVector v) {
    JonesVector res;
    res.ex = complex_add(complex_mul(M.m00, v.ex), complex_mul(M.m01, v.ey));
    res.ey = complex_add(complex_mul(M.m10, v.ex), complex_mul(M.m11, v.ey));
    return res;
}

/* Матриця лінійного поляризатора під кутом theta (рад) */
JonesMatrix jones_polarizer(double theta_rad) {
    double c = cos(theta_rad);
    double s = sin(theta_rad);
    JonesMatrix M;
    M.m00 = complex_create(c * c, 0.0);
    M.m01 = complex_create(c * s, 0.0);
    M.m10 = complex_create(c * s, 0.0);
    M.m11 = complex_create(s * s, 0.0);
    return M;
}

/* Матриця фазового затримувача (пластинки) з фазою phi та орієнтацією theta */
JonesMatrix jones_retarder(double theta_rad, double phi_rad) {
    double c = cos(theta_rad);
    double s = sin(theta_rad);
    Complex e_neg = complex_create(cos(-phi_rad / 2.0), sin(-phi_rad / 2.0));
    Complex e_pos = complex_create(cos(phi_rad / 2.0), sin(phi_rad / 2.0));

    Complex c2 = complex_create(c * c, 0.0);
    Complex s2 = complex_create(s * s, 0.0);
    Complex cs = complex_create(c * s, 0.0);

    JonesMatrix M;
    M.m00 = complex_add(complex_mul(c2, e_neg), complex_mul(s2, e_pos));
    M.m01 = complex_mul(cs, complex_sub(e_neg, e_pos));
    M.m10 = M.m01;
    M.m11 = complex_add(complex_mul(s2, e_neg), complex_mul(c2, e_pos));
    return M;
}

int main(void) {
    printf("=== Симуляція оптичного тракту (C99) ===\n");
    
    /* 1. Початкове світло: лінійно поляризоване під 0 градусів (горизонтальне) */
    JonesVector in_wave = jones_vector_linear(1.0, 0.0);
    double i0 = jones_intensity(in_wave);
    printf("Початкова інтенсивність I0 = %.4f\n", i0);

    /* 2. Проходження крізь чвертьхвильову пластинку (λ/4) під кутом 45 град */
    JonesMatrix qwp = jones_retarder(45.0 * M_PI / 180.0, M_PI / 2.0);
    JonesVector after_qwp = jones_apply(qwp, in_wave);
    printf("Інтенсивність після λ/4 пластинки = %.4f\n", jones_intensity(after_qwp));

    /* 3. Проходження крізь поворотний аналізатор під кутами від 0 до 180 град */
    printf("\nПеревірка закону Малюса після поляризаційного тракту:\n");
    printf("Кут (град) | Інтенсивність I | Теорія I_exp\n");
    printf("-------------------------------------------\n");
    
    for (int deg = 0; deg <= 180; deg += 30) {
        double rad = deg * M_PI / 180.0;
        JonesMatrix analyzer = jones_polarizer(rad);
        JonesVector out_wave = jones_apply(analyzer, after_qwp);
        double i_out = jones_intensity(out_wave);
        printf("  %3d°     |     %.4f     |    0.5000\n", deg, i_out);
    }

    return 0;
}
