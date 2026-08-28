#include <cmath>
#include <cstdio>

int main() {
    // система (СІ)
    const double m = 1.0, k = 100.0, g = 9.8;
    const double mu_s = 0.5, mu_k = 0.3;      // тертя спокою / ковзання
    const double V = 0.02;                    // швидкість тяги (м/с)
    const double dt = 1e-4, T = 8.0;
    const double N = m*g, Fs = mu_s*N, Fk = mu_k*N;

    double x = 0.0, v = 0.0, v_peak = 0.0;
    bool   stuck = true;                       // режим руху
    double t_last_break = -1.0, period = 0.0;

    for (double t = 0.0; t < T; t += dt) {
        const double F = k*(V*t - x);          // сила пружини
        if (stuck) {
            if (F >= Fs) {                     // ЗРИВ
                stuck = false;
                if (t_last_break >= 0.0) period = t - t_last_break;
                t_last_break = t;
            }
        } else {
            const double fric = (v >= 0.0 ? Fk : -Fk);
            const double a = (F - fric) / m;   // другий закон Ньютона
            v += a*dt;                         // напівнеявний Ейлер
            x += v*dt;
            if (v > v_peak) v_peak = v;
            if (v <= 0.0) { v = 0.0; stuck = true; }  // прилип знову
        }
    }
    std::printf("період ≈ %.2f с (%.2f Гц),  пік кидка = %.3f м/с (%.0f·V)\n",
                period, 1.0/period, v_peak, v_peak/V);
    return 0;
}
