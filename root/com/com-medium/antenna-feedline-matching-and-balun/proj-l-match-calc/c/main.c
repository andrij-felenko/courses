#include <stdio.h>
#include <math.h>
#include <stdbool.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef enum {
    ELEMENT_CAPACITOR,
    ELEMENT_INDUCTOR
} ElementType;

typedef struct {
    ElementType type;
    double value; /* Фаради або Генрі */
} ReactiveElement;

typedef struct {
    char name[64];
    bool valid;
    ReactiveElement series_elem;  /* Послідовний елемент X_s */
    ReactiveElement parallel_elem;/* Паралельний елемент B_p */
} LMatchSolution;

typedef struct {
    LMatchSolution low_pass;
    LMatchSolution high_pass;
} LMatchResult;

static ReactiveElement reactance_to_element(double X, double freq_hz) {
    ReactiveElement elem;
    double omega = 2.0 * M_PI * freq_hz;
    if (X >= 0.0) {
        elem.type = ELEMENT_INDUCTOR;
        elem.value = X / omega;
    } else {
        elem.type = ELEMENT_CAPACITOR;
        elem.value = 1.0 / (omega * fabs(X));
    }
    return elem;
}

static ReactiveElement susceptance_to_element(double B, double freq_hz) {
    ReactiveElement elem;
    double omega = 2.0 * M_PI * freq_hz;
    if (B >= 0.0) {
        elem.type = ELEMENT_CAPACITOR;
        elem.value = B / omega;
    } else {
        elem.type = ELEMENT_INDUCTOR;
        elem.value = 1.0 / (omega * fabs(B));
    }
    return elem;
}

LMatchResult calculate_l_match(double freq_hz, double Z0, double R_A, double X_A) {
    LMatchResult res;
    res.low_pass.valid = false;
    res.high_pass.valid = false;

    if (R_A <= 0.0 || Z0 <= 0.0 || freq_hz <= 0.0) {
        return res;
    }

    if (R_A > Z0) {
        /* Топологія А: Паралельний елемент B_p біля антени R_A */
        double Q = sqrt((R_A / Z0) - 1.0);
        double Rsq_plus_Xsq = R_A * R_A + X_A * X_A;

        /* Розв'язок 1: ФНЧ (+Q) */
        double B_p1 = (-X_A + R_A * Q) / Rsq_plus_Xsq;
        double X_s1 = Z0 * Q;
        
        snprintf(res.low_pass.name, sizeof(res.low_pass.name), "Топологія А (ФНЧ / Low-pass)");
        res.low_pass.valid = true;
        res.low_pass.series_elem = reactance_to_element(X_s1, freq_hz);
        res.low_pass.parallel_elem = susceptance_to_element(B_p1, freq_hz);

        /* Розв'язок 2: ФВЧ (-Q) */
        double B_p2 = (-X_A - R_A * Q) / Rsq_plus_Xsq;
        double X_s2 = -Z0 * Q;

        snprintf(res.high_pass.name, sizeof(res.high_pass.name), "Топологія А (ФВЧ / High-pass)");
        res.high_pass.valid = true;
        res.high_pass.series_elem = reactance_to_element(X_s2, freq_hz);
        res.high_pass.parallel_elem = susceptance_to_element(B_p2, freq_hz);

    } else {
        /* Топологія Б: Паралельний елемент B_p біля фідеру Z0 */
        double Q = sqrt((Z0 / R_A) - 1.0);

        /* Розв'язок 1: ФНЧ */
        double X_s1 = -X_A + R_A * Q;
        double B_p1 = Q / Z0;

        snprintf(res.low_pass.name, sizeof(res.low_pass.name), "Топологія Б (ФНЧ / Low-pass)");
        res.low_pass.valid = true;
        res.low_pass.series_elem = reactance_to_element(X_s1, freq_hz);
        res.low_pass.parallel_elem = susceptance_to_element(B_p1, freq_hz);

        /* Розв'язок 2: ФВЧ */
        double X_s2 = -X_A - R_A * Q;
        double B_p2 = -Q / Z0;

        snprintf(res.high_pass.name, sizeof(res.high_pass.name), "Топологія Б (ФВЧ / High-pass)");
        res.high_pass.valid = true;
        res.high_pass.series_elem = reactance_to_element(X_s2, freq_hz);
        res.high_pass.parallel_elem = susceptance_to_element(B_p2, freq_hz);
    }

    return res;
}

static void print_solution(const LMatchSolution* sol) {
    if (!sol->valid) {
        printf("  [Помилка розрахунку: некоректні вхідні параметри]\n");
        return;
    }
    printf("--- %s ---\n", sol->name);
    
    if (sol->series_elem.type == ELEMENT_INDUCTOR) {
        printf("  Послідовний елемент: L_series   = %.2f нГн\n", sol->series_elem.value * 1e9);
    } else {
        printf("  Послідовний елемент: C_series   = %.2f пФ\n", sol->series_elem.value * 1e12);
    }

    if (sol->parallel_elem.type == ELEMENT_INDUCTOR) {
        printf("  Паралельний елемент: L_parallel = %.2f нГн\n", sol->parallel_elem.value * 1e9);
    } else {
        printf("  Паралельний елемент: C_parallel = %.2f пФ\n", sol->parallel_elem.value * 1e12);
    }
}

int main(void) {
    double freq_hz = 145.0e6; /* 145 МГц (2м аматорський радіодіапазон) */
    double Z0 = 50.0;
    double R_A = 15.0;        /* Укорочений штир: R_A = 15 Ом */
    double X_A = -45.0;       /* Ємнісна реактивність: X_A = -45 Ом */

    printf("Розрахунок L-вузла для f = %.1f МГц, Z0 = %.1f Ом, Z_A = %.1f %+.1fj Ом\n\n",
           freq_hz / 1e6, Z0, R_A, X_A);

    LMatchResult res = calculate_l_match(freq_hz, Z0, R_A, X_A);
    print_solution(&res.low_pass);
    printf("\n");
    print_solution(&res.high_pass);

    return 0;
}
