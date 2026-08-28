/* quantum_well_solver.c — Чисельний солвер квантових ям на C */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define PI 3.14159265358979323846
#define HBAR_EV_S 6.582119569e-16 /* ℏ в еВ·с */
#define M0_KG 9.1093837015e-31    /* Маса вільного електрона в кг */
#define EV_TO_J 1.602176634e-19   /* Переклад еВ -> Дж */
#define HBAR_J_S 1.054571817e-34  /* ℏ в Дж·с */

typedef struct {
    int N;             /* Кількість вузлів сітки */
    double L_z;        /* Фізична ширина області в метрах */
    double dz;         /* Крок сітки Δz */
    double *z;         /* Масив координат z */
    double *V;         /* Потенціал V(z) в еВ */
    double *m_eff;     /* Відносна ефективна маса m*(z)/m0 */
    double *diag;      /* Головна діагональ матриці Гамільтона H */
    double *subdiag;   /* Побічна діагональ H */
} QuantumWellGrid;

/* Ініціалізація сітки та виділення пам'яті */
QuantumWellGrid* create_grid(int N, double L_z) {
    QuantumWellGrid *g = (QuantumWellGrid*)malloc(sizeof(QuantumWellGrid));
    if (!g) return NULL;
    g->N = N;
    g->L_z = L_z;
    g->dz = L_z / (N - 1);
    g->z = (double*)calloc(N, sizeof(double));
    g->V = (double*)calloc(N, sizeof(double));
    g->m_eff = (double*)calloc(N, sizeof(double));
    g->diag = (double*)calloc(N, sizeof(double));
    g->subdiag = (double*)calloc(N, sizeof(double));
    
    for (int i = 0; i < N; i++) {
        g->z[i] = -L_z / 2.0 + i * g->dz;
    }
    return g;
}

void free_grid(QuantumWellGrid *g) {
    if (!g) return;
    free(g->z); free(g->V); free(g->m_eff);
    free(g->diag); free(g->subdiag);
    free(g);
}

/* Заповнення оператора Гамільтона */
void build_hamiltonian(QuantumWellGrid *g, double electric_field_V_m) {
    double dz = g->dz;
    /* Константа C0 = ℏ² / (2 * m0 * dz²) в еВ */
    double C0 = (HBAR_J_S * HBAR_J_S) / (2.0 * M0_KG * dz * dz * EV_TO_J);

    for (int i = 1; i < g->N - 1; i++) {
        double m_left  = 0.5 * (g->m_eff[i-1] + g->m_eff[i]);
        double m_right = 0.5 * (g->m_eff[i]   + g->m_eff[i+1]);
        
        double A_i = C0 / m_left;
        double C_i = C0 / m_right;
        
        /* Враховуємо потенціал ями V(z) та нахил електричного поля (e * F * z) */
        double V_field = electric_field_V_m * g->z[i];
        g->diag[i] = A_i + C_i + g->V[i] + V_field;
        g->subdiag[i] = -C_i;
    }
}

/* Швидкий розв'язувач тридіагональної системи методом Томаса */
void solve_tridiagonal(int N, const double *a, const double *b, const double *c, const double *rhs, double *x) {
    double *cp = (double*)malloc(N * sizeof(double));
    double *dp = (double*)malloc(N * sizeof(double));

    cp[1] = c[1] / b[1];
    dp[1] = rhs[1] / b[1];

    for (int i = 2; i < N - 1; i++) {
        double denom = b[i] - a[i] * cp[i-1];
        cp[i] = c[i] / denom;
        dp[i] = (rhs[i] - a[i] * dp[i-1]) / denom;
    }

    x[N-2] = dp[N-2];
    for (int i = N - 3; i >= 1; i--) {
        x[i] = dp[i] - cp[i] * x[i+1];
    }

    free(cp); free(dp);
}

/* Обернена степенева ітерація для шуканого рівня E_shift */
double solve_eigenstate(QuantumWellGrid *g, double E_shift, double *psi, int max_iter, double tol) {
    int N = g->N;
    double *b = (double*)malloc(N * sizeof(double));
    double *rhs = (double*)malloc(N * sizeof(double));

    /* Ініціалізація початкового наближення хвильової функції */
    for (int i = 1; i < N - 1; i++) {
        psi[i] = sin(PI * i / (N - 1));
        rhs[i] = psi[i];
    }
    psi[0] = psi[N-1] = 0.0;

    double E_old = 0.0;
    double E_new = 0.0;

    for (int iter = 0; iter < max_iter; iter++) {
        for (int i = 1; i < N - 1; i++) {
            b[i] = g->diag[i] - E_shift;
        }

        solve_tridiagonal(N, g->subdiag, b, g->subdiag, rhs, psi);

        /* Нормування вектора ψ */
        double norm = 0.0;
        for (int i = 1; i < N - 1; i++) {
            norm += psi[i] * psi[i] * g->dz;
        }
        norm = sqrt(norm);
        for (int i = 1; i < N - 1; i++) {
            psi[i] /= norm;
        }

        /* Обчислення відношення Релея для оцінки E_new */
        E_new = 0.0;
        for (int i = 1; i < N - 1; i++) {
            double H_psi = g->diag[i] * psi[i] + g->subdiag[i-1] * psi[i-1] + g->subdiag[i] * psi[i+1];
            E_new += psi[i] * H_psi * g->dz;
        }

        if (fabs(E_new - E_old) < tol) break;
        E_old = E_new;

        for (int i = 1; i < N - 1; i++) rhs[i] = psi[i];
    }

    free(b); free(rhs);
    return E_new;
}

int main(void) {
    int N = 501;
    double L_z = 30.0e-9; /* 30 нм розрахункове вікно */
    double QW_width = 10.0e-9; /* 10 нм яма GaAs */

    QuantumWellGrid *g = create_grid(N, L_z);
    if (!g) return 1;

    /* Задаємо профіль GaAs/Al0.3Ga0.7As ями */
    for (int i = 0; i < N; i++) {
        if (fabs(g->z[i]) <= QW_width / 2.0) {
            g->V[i] = 0.0;          /* Дно ями GaAs */
            g->m_eff[i] = 0.067;    /* m* електрона в GaAs */
        } else {
            g->V[i] = 0.224;        /* Бар'єр Al0.3Ga0.7As (ΔEc = 224 меВ) */
            g->m_eff[i] = 0.092;    /* m* в AlGaAs */
        }
    }

    build_hamiltonian(g, 0.0); /* Поле F = 0 */

    double *psi = (double*)calloc(N, sizeof(double));
    double E1 = solve_eigenstate(g, 0.05, psi, 1000, 1e-7);

    printf("--- РЕЗУЛЬТАТИ ОБЧИСЛЕННЯ КВАНТОВОЇ ЯМИ (C) ---\n");
    printf("Ширина ями L_z: %.1f нм\n", QW_width * 1e9);
    printf("Енергія основного стану E_1: %.3f меВ (від дна ями)\n", E1 * 1000.0);

    free(psi);
    free_grid(g);
    return 0;
}
