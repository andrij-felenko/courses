#include <stdio.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

// Структура комплексного числа для мови C
typedef struct {
    double re;
    double im;
} Complex;

// Арифметика комплексних чисел
Complex c_make(double re, double im) {
    return (Complex){re, im};
}

Complex c_add(Complex a, Complex b) {
    return (Complex){a.re + b.re, a.im + b.im};
}

Complex c_sub(Complex a, Complex b) {
    return (Complex){a.re - b.re, a.im - b.im};
}

Complex c_mul(Complex a, Complex b) {
    return (Complex){a.re * b.re - a.im * b.im, a.re * b.im + a.im * b.re};
}

Complex c_div(Complex a, Complex b) {
    double denom = b.re * b.re + b.im * b.im;
    if (denom < 1e-15) return (Complex){0.0, 0.0};
    return (Complex){(a.re * b.re + a.im * b.im) / denom, (a.im * b.re - a.re * b.im) / denom};
}

Complex c_conj(Complex a) {
    return (Complex){a.re, -a.im};
}

double c_abs(Complex a) {
    return sqrt(a.re * a.re + a.im * a.im);
}

double c_arg(Complex a) {
    return atan2(a.im, a.re);
}

// Вхідні дані трифазної системи
typedef struct {
    double v_line;        // Лінійна напруга (В)
    double f_hz;          // Частота мережі (Гц)
    Complex z_a;          // Комплексний опір фази A (Ом)
    Complex z_b;          // Комплексний опір фази B (Ом)
    Complex z_c;          // Комплексний опір фази C (Ом)
    Complex z_n;          // Комплексний опір нейтрального провідника (Ом)
    int has_neutral;      // Прапорець наявності нейтралі (1 - є, 0 - нема)
} ThreePhaseSystem;

// Результати розрахунку
typedef struct {
    Complex u_source[3];  // Фазні ЕРС джерела A, B, C
    Complex u_n;          // Напруга зміщення нейтралі UN
    Complex u_load[3];    // Фактичні напруги на фазах навантаження
    Complex i_phase[3];   // Струми у фазах навантаження
    Complex i_n;          // Струм у нейтральному провіднику
    double p_phase[3];    // Активні потужності фаз
    double q_phase[3];    // Реактивні потужності фаз
    double p_total;       // Повна активна потужність трифазної системи
    double q_total;       // Повна реактивна потужність
    double s_total;       // Повна потужність
} ThreePhaseResult;

// Основний розрахунковий модуль
ThreePhaseResult solve_three_phase_star(const ThreePhaseSystem* sys) {
    ThreePhaseResult res;
    double v_ph = sys->v_line / sqrt(3.0);
    
    // 1. Формування фазних ЕРС джерела (зсув 120 градусів)
    res.u_source[0] = c_make(v_ph, 0.0);
    res.u_source[1] = c_make(-0.5 * v_ph, -sqrt(3.0) / 2.0 * v_ph);
    res.u_source[2] = c_make(-0.5 * v_ph, sqrt(3.0) / 2.0 * v_ph);
    
    // 2. Обчислення комплексних провідностей фаз Y = 1 / Z
    Complex y_a = c_div(c_make(1.0, 0.0), sys->z_a);
    Complex y_b = c_div(c_make(1.0, 0.0), sys->z_b);
    Complex y_c = c_div(c_make(1.0, 0.0), sys->z_c);
    
    // 3. Розрахунок зміщення нейтралі UN за формулою Мілмана
    if (sys->has_neutral) {
        Complex y_n = c_div(c_make(1.0, 0.0), sys->z_n);
        Complex num = c_add(c_add(c_mul(res.u_source[0], y_a), c_mul(res.u_source[1], y_b)), c_mul(res.u_source[2], y_c));
        Complex den = c_add(c_add(c_add(y_a, y_b), y_c), y_n);
        res.u_n = c_div(num, den);
        res.i_n = c_mul(res.u_n, y_n);
    } else {
        Complex num = c_add(c_add(c_mul(res.u_source[0], y_a), c_mul(res.u_source[1], y_b)), c_mul(res.u_source[2], y_c));
        Complex den = c_add(c_add(y_a, y_b), y_c);
        res.u_n = c_div(num, den);
        res.i_n = c_make(0.0, 0.0);
    }
    
    // 4. Напруги та струми на фазах споживача
    res.p_total = 0.0;
    res.q_total = 0.0;
    
    for (int k = 0; k < 3; ++k) {
        res.u_load[k] = c_sub(res.u_source[k], res.u_n);
        Complex y_k = (k == 0) ? y_a : (k == 1) ? y_b : y_c;
        res.i_phase[k] = c_mul(res.u_load[k], y_k);
        
        // Потужність фази S = U * conj(I)
        Complex s_k = c_mul(res.u_load[k], c_conj(res.i_phase[k]));
        res.p_phase[k] = s_k.re;
        res.q_phase[k] = s_k.im;
        
        res.p_total += res.p_phase[k];
        res.q_total += res.q_phase[k];
    }
    
    res.s_total = sqrt(res.p_total * res.p_total + res.q_total * res.q_total);
    return res;
}

void print_result_c(const ThreePhaseResult* r) {
    printf("===================================================\n");
    printf("   РЕЗУЛЬТАТИ РОЗРАХУНКУ ТРИФАЗНОЇ СИСТЕМИ (C)\n");
    printf("===================================================\n");
    printf("Зміщення нейтралі UN: %6.2f V, кут: %6.1f deg\n", c_abs(r->u_n), c_arg(r->u_n) * 180.0 / M_PI);
    printf("Струм у нейтралі  IN: %6.2f A, кут: %6.1f deg\n", c_abs(r->i_n), c_arg(r->i_n) * 180.0 / M_PI);
    printf("---------------------------------------------------\n");
    for (int i = 0; i < 3; ++i) {
        char phase = 'A' + i;
        printf("Фаза %c: U' = %6.2f V, I = %6.2f A, P = %7.1f W, Q = %7.1f VAR\n",
               phase, c_abs(r->u_load[i]), c_abs(r->i_phase[i]), r->p_phase[i], r->q_phase[i]);
    }
    printf("---------------------------------------------------\n");
    printf("Повна активна потужність   P_total: %8.1f W\n", r->p_total);
    printf("Повна реактивна потужність Q_total: %8.1f VAR\n", r->q_total);
    printf("Повна потужність системи   S_total: %8.1f VA\n", r->s_total);
    printf("===================================================\n");
}

int main(void) {
    ThreePhaseSystem sys = {
        .v_line = 400.0,
        .f_hz = 50.0,
        .z_a = {10.0, 0.0},     // 10 Ом чисто активне
        .z_b = {15.0, 10.0},    // 15 + j10 Ом індуктивне
        .z_c = {20.0, -8.0},    // 20 - j8 Ом ємнісне
        .z_n = {1.2, 0.0},      // 1.2 Ом опір нейтрального проводу
        .has_neutral = 1
    };
    
    ThreePhaseResult r = solve_three_phase_star(&sys);
    print_result_c(&r);
    return 0;
}
