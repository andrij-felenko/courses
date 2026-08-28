#include <stdio.h>
#include <math.h>

// Заряд RC двома методами інтегрування проти точної формули.
// Показує, чому трапеція (2-й порядок) б'є різницю назад (1-й) на тому ж кроці.
int main(void) {
    const double tau = 1e-3;     // стала часу RC = 1 мс
    const double dt  = 1e-4;     // крок 0.1 мс
    double u_be = 0.0, u_tr = 0.0;   // напруга: різниця назад / трапеція
    const double a = dt / (2.0 * tau);   // множник трапеції a = Δt/2τ

    printf("  t,мс   точна    BE      TR    |  похибка BE  похибка TR\n");
    for (int n = 1; n <= 10; n++) {
        double t = n * dt;
        double u_exact = 1.0 - exp(-t / tau);          // еталон

        // різниця назад: Uₙ₊₁ = Uₙ + dt·(1−Uₙ₊₁)/tau  → розв'язуємо явно
        u_be = (u_be + dt / tau) / (1.0 + dt / tau);

        // трапеція: Uₙ₊₁ = Uₙ + (dt/2)·[(1−Uₙ)/tau + (1−Uₙ₊₁)/tau]
        //           → розкрито:  Uₙ₊₁ = [Uₙ(1−a) + 2a] / (1+a)
        u_tr = (u_tr * (1.0 - a) + 2.0 * a) / (1.0 + a);

        printf("%5.1f  %.4f  %.4f  %.4f  |  %+.5f    %+.5f\n",
               t * 1e3, u_exact, u_be, u_tr,
               u_be - u_exact, u_tr - u_exact);
    }
    return 0;
}
