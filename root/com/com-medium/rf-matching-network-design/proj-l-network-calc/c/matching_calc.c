/* c/matching_calc.c — Калькулятор та симулятор L-ланок мовою C (C99/C11) */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef struct {
    double real;
    double imag;
} Complex_t;

static Complex_t c_add(Complex_t a, Complex_t b) {
    return (Complex_t){a.real + b.real, a.imag + b.imag};
}

static Complex_t c_sub(Complex_t a, Complex_t b) {
    return (Complex_t){a.real - b.real, a.imag - b.imag};
}

static Complex_t c_mul(Complex_t a, Complex_t b) {
    return (Complex_t){a.real * b.real - a.imag * b.imag, a.real * b.imag + a.imag * b.real};
}

static Complex_t c_div(Complex_t a, Complex_t b) {
    double denom = b.real * b.real + b.imag * b.imag;
    return (Complex_t){(a.real * b.real + a.imag * b.imag) / denom,
                       (a.imag * b.real - a.real * b.imag) / denom};
}

static double c_abs(Complex_t a) {
    return sqrt(a.real * a.real + a.imag * a.imag);
}

typedef enum {
    TOPOLOGY_LOWPASS_STEP_DOWN = 0,
    TOPOLOGY_LOWPASS_STEP_UP,
    TOPOLOGY_HIGHPASS_STEP_DOWN,
    TOPOLOGY_HIGHPASS_STEP_UP
} TopologyType_t;

typedef struct {
    TopologyType_t type;
    double L_henry;
    double C_farad;
    double Q_network;
    bool valid;
} MatchingResult_t;

/* Синтез L-ланки для чисто активних опорів R_S та R_L */
MatchingResult_t calculate_l_network(double R_S, double R_L, double freq_hz, bool is_lowpass) {
    MatchingResult_t res = {0};
    if (R_S <= 0.0 || R_L <= 0.0 || freq_hz <= 0.0) {
        res.valid = false;
        return res;
    }

    double omega0 = 2.0 * M_PI * freq_hz;
    double R_high = (R_S > R_L) ? R_S : R_L;
    double R_low  = (R_S > R_L) ? R_L : R_S;

    double Q_sq = (R_high / R_low) - 1.0;
    if (Q_sq < 0.0) {
        res.valid = false;
        return res;
    }
    double Q = sqrt(Q_sq);
    res.Q_network = Q;
    res.valid = true;

    double X_series = Q * R_low;
    double X_parallel = R_high / Q;

    if (R_S > R_L) {
        /* Знижувальна ланка: паралельний елемент біля R_S, послідовний біля R_L */
        if (is_lowpass) {
            res.type = TOPOLOGY_LOWPASS_STEP_DOWN;
            res.C_farad = 1.0 / (omega0 * X_parallel);
            res.L_henry = X_series / omega0;
        } else {
            res.type = TOPOLOGY_HIGHPASS_STEP_DOWN;
            res.L_henry = X_parallel / omega0;
            res.C_farad = 1.0 / (omega0 * X_series);
        }
    } else {
        /* Підвищувальна ланка: послідовний елемент біля R_S, паралельний біля R_L */
        if (is_lowpass) {
            res.type = TOPOLOGY_LOWPASS_STEP_UP;
            res.L_henry = X_series / omega0;
            res.C_farad = 1.0 / (omega0 * X_parallel);
        } else {
            res.type = TOPOLOGY_HIGHPASS_STEP_UP;
            res.C_farad = 1.0 / (omega0 * X_series);
            res.L_henry = X_parallel / omega0;
        }
    }

    return res;
}

/* Обчислення вхідного імпедансу ФНЧ підвищувальної L-ланки на частоті f */
Complex_t calculate_zin_lowpass_step_up(double R_L, double L_h, double C_f, double f_hz, double Q_inductor) {
    double omega = 2.0 * M_PI * f_hz;
    
    /* Паралельне з'єднання R_L та C */
    Complex_t Z_load = {R_L, 0.0};
    Complex_t Z_cap = {0.0, -1.0 / (omega * C_f)};
    
    Complex_t Z_parallel = c_div(c_mul(Z_load, Z_cap), c_add(Z_load, Z_cap));
    
    /* Послідовна індуктивність із урахуванням активних втрат R_ESR */
    double R_esr = (Q_inductor > 0.0) ? (omega * L_h / Q_inductor) : 0.0;
    Complex_t Z_ind = {R_esr, omega * L_h};
    
    return c_add(Z_parallel, Z_ind);
}

int main(void) {
    double R_S = 10.0;       /* Опір передавача (10 Ом) */
    double R_L = 50.0;       /* Опір антени (50 Ом) */
    double f0  = 433.92e6;   /* Робоча частота 433.92 МГц */

    printf("=== КАЛЬКУЛЯТОР L-ЛАНОК (C99) ===\n");
    printf("Джерело R_S = %.1f Ом | Навантаження R_L = %.1f Ом | f0 = %.2f МГц\n",
           R_S, R_L, f0 / 1e6);

    MatchingResult_t res = calculate_l_network(R_S, R_L, f0, true);
    if (!res.valid) {
        printf("Помилка: неможливо розрахувати узгодження!\n");
        return 1;
    }

    printf("\nРезультат розрахунку (ФНЧ підвищувальний):\n");
    printf("  Добротність кола Q  = %.3f\n", res.Q_network);
    printf("  Індуктивність L     = %.3f нГн\n", res.L_henry * 1e9);
    printf("  Ємність C           = %.3f пФ\n", res.C_farad * 1e12);

    printf("\n--- ЧАСТОТНИЙ СИМУЛЯТОР КСХ (VSWR Sweep) ---\n");
    printf(" Частота (МГц) | Zin (Ом)        | |S11|   |  КСХ (VSWR)\n");
    printf("---------------+-----------------+---------+-------------\n");

    double f_start = f0 * 0.8;
    double f_end   = f0 * 1.2;
    int steps = 9;
    double f_step = (f_end - f_start) / (steps - 1);

    for (int i = 0; i < steps; ++i) {
        double f = f_start + i * f_step;
        Complex_t Zin = calculate_zin_lowpass_step_up(R_L, res.L_henry, res.C_farad, f, 80.0);
        
        /* Обчислення S11 відносно R_S */
        Complex_t num = c_sub(Zin, (Complex_t){R_S, 0.0});
        Complex_t den = c_add(Zin, (Complex_t){R_S, 0.0});
        Complex_t S11 = c_div(num, den);
        double gamma = c_abs(S11);
        
        double vswr = (gamma >= 0.999) ? 99.9 : ((1.0 + gamma) / (1.0 - gamma));
        
        printf("  %11.2f | %6.2f + j%6.2f | %7.4f | %11.2f\n",
               f / 1e6, Zin.real, Zin.imag, gamma, vswr);
    }

    return 0;
}
