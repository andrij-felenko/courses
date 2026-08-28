#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define NX 200
#define STEPS 400

typedef struct {
    double Ez[NX];
    double Hy[NX - 1];
    double eps_r[NX];
    double dx;
    double dt;
    double ch;
} Fdtd1DCContext;

void fdtd_init(Fdtd1DCContext* ctx, double dx) {
    const double c0 = 299792458.0;
    const double eps0 = 8.854187817e-12;
    const double mu0 = 4.0 * M_PI * 1e-7;

    ctx->dx = dx;
    ctx->dt = dx / (2.0 * c0);
    ctx->ch = ctx->dt / (mu0 * dx);

    for (int i = 0; i < NX; ++i) {
        ctx->Ez[i] = 0.0;
        ctx->eps_r[i] = (i >= 80 && i < 120) ? 4.0 : 1.0;
    }
    for (int i = 0; i < NX - 1; ++i) {
        ctx->Hy[i] = 0.0;
    }
}

void fdtd_step(Fdtd1DCContext* ctx, int t_step) {
    const double eps0 = 8.854187817e-12;

    /* 1. Оновлення поля Hy */
    for (int k = 0; k < NX - 1; ++k) {
        ctx->Hy[k] += ctx->ch * (ctx->Ez[k + 1] - ctx->Ez[k]);
    }

    /* 2. Оновлення поля Ez (урахування струму зміщення) */
    for (int k = 1; k < NX - 1; ++k) {
        double ce = ctx->dt / (eps0 * ctx->eps_r[k] * ctx->dx);
        ctx->Ez[k] += ce * (ctx->Hy[k] - ctx->Hy[k - 1]);
    }

    /* 3. Гауссів імпульсний джерельний сигнал */
    double pulse = exp(-pow(((double)t_step - 40.0) / 12.0, 2));
    ctx->Ez[30] += pulse;
}

int main(void) {
    Fdtd1DCContext ctx;
    fdtd_init(&ctx, 1e-3);

    printf("Запуск симулятора FDTD (C): dt = %.2f пс\n", ctx.dt * 1e12);

    for (int t = 0; t < STEPS; ++t) {
        fdtd_step(&ctx, t);
    }

    double max_ez = 0.0;
    for (int i = 80; i < 120; ++i) {
        if (fabs(ctx.Ez[i]) > max_ez) {
            max_ez = fabs(ctx.Ez[i]);
        }
    }

    printf("Максимальна амплітуда Ez у конденсаторі: %.4f В/м\n", max_ez);
    return 0;
}
