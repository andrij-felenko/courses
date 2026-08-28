#include <stdio.h>
#include <stdlib.h>
#include <math.h>

typedef struct {
    double W;        /* Товщина напівпровідника, см */
    double D;        /* Коефіцієнт дифузії, см²/с */
    double tau;      /* Час життя носіїв, с */
    double G0;       /* Початкова швидкість генерації світлом, см⁻³с⁻¹ */
    double alpha;    /* Коефіцієнт поглинання світла, см⁻¹ */
    double dn_surf;  /* Поверхнева концентрація носіїв при x=0, см⁻³ */
} SimParams;

/* Алгоритм прогонки (TDMA) для тридіагональної матриці */
void solve_diffusion_1d(const SimParams *p, int N, double *x, double *dn) {
    double h = p->W / (N - 1);
    double L = sqrt(p->D * p->tau);
    double gamma = (h * h) / (L * L);
    double h2_D = (h * h) / p->D;

    double *a = (double *)malloc(N * sizeof(double));
    double *b = (double *)malloc(N * sizeof(double));
    double *c = (double *)malloc(N * sizeof(double));
    double *d = (double *)malloc(N * sizeof(double));
    double *c_star = (double *)malloc(N * sizeof(double));
    double *d_star = (double *)malloc(N * sizeof(double));

    /* Створення сітки x_i та заповнення системи рівнянь */
    for (int i = 0; i < N; ++i) {
        x[i] = i * h;
        double G_i = p->G0 * exp(-p->alpha * x[i]); /* Експоненціальне поглинання світла */

        if (i == 0) {
            /* Гранична умова x = 0: задана концентрація інжекції */
            b[i] = 1.0;
            c[i] = 0.0;
            d[i] = p->dn_surf;
        } else if (i == N - 1) {
            /* Гранична умова x = W: ідеальний сток (перехід) */
            a[i] = 0.0;
            b[i] = 1.0;
            d[i] = 0.0;
        } else {
            a[i] = 1.0;
            b[i] = -(2.0 + gamma);
            c[i] = 1.0;
            d[i] = -h2_D * G_i;
        }
    }

    /* Прямий хід прогонки */
    c_star[0] = c[0] / b[0];
    d_star[0] = d[0] / b[0];
    for (int i = 1; i < N; ++i) {
        double m = b[i] - a[i] * c_star[i - 1];
        c_star[i] = c[i] / m;
        d_star[i] = (d[i] - a[i] * d_star[i - 1]) / m;
    }

    /* Зворотний хід прогонки */
    dn[N - 1] = d_star[N - 1];
    for (int i = N - 2; i >= 0; --i) {
        dn[i] = d_star[i] - c_star[i] * dn[i + 1];
    }

    free(a); free(b); free(c); free(d);
    free(c_star); free(d_star);
}

int main(void) {
    SimParams p = {
        .W = 0.02,        /* 200 мкм товщина */
        .D = 35.0,        /* 35 см²/с для електронів у кремнії */
        .tau = 10e-6,     /* 10 мкс час життя */
        .G0 = 1e20,       /* Фотогенерація світлом */
        .alpha = 500.0,   /* 500 см⁻¹ */
        .dn_surf = 1e14   /* Інжекція на поверхні */
    };
    int N = 101;
    double *x = (double *)malloc(N * sizeof(double));
    double *dn = (double *)malloc(N * sizeof(double));

    solve_diffusion_1d(&p, N, x, dn);

    double L = sqrt(p.D * p.tau);
    printf("Дифузійна довжина L = %.2f мкм\n", L * 1e4);
    printf("Вузол\tx (мкм)\t\tΔn (см⁻³)\n");
    for (int i = 0; i < N; i += 20) {
        printf("%d\t%.2f\t\t%.3e\n", i, x[i] * 1e4, dn[i]);
    }

    free(x); free(dn);
    return 0;
}
