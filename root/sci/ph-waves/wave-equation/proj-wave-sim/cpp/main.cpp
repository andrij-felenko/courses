#include <cstdio>
#include <vector>

enum class End { Fixed, Free };            // закріплений / вільний кінець

struct StringSim {
    std::vector<double> prev, cur, next;   // стани в моменти t−Δt, t, t+Δt
    double r2;                             // (c·Δt/Δx)²
    End left, right;

    StringSim(int nodes, double r, End l, End rt)
        : prev(nodes, 0.0), cur(nodes, 0.0), next(nodes, 0.0),
          r2(r * r), left(l), right(rt) {}

    // старт: фізика дає форму й швидкість, а схемі потрібні ДВА готові стани
    void start(const std::vector<double> &y0, const std::vector<double> &v0, double dt) {
        const int N = static_cast<int>(cur.size()) - 1;
        prev = y0;
        for (int i = 1; i < N; ++i)
            cur[i] = y0[i] + dt * v0[i]
                   + 0.5 * r2 * (y0[i - 1] - 2.0 * y0[i] + y0[i + 1]);   // ПОЛОВИННА поправка
        cur[0] = (left  == End::Fixed) ? 0.0 : y0[0] + dt * v0[0] + r2 * (y0[1] - y0[0]);
        cur[N] = (right == End::Fixed) ? 0.0 : y0[N] + dt * v0[N] + r2 * (y0[N - 1] - y0[N]);
        if (left  == End::Fixed) prev[0] = 0.0;
        if (right == End::Fixed) prev[N] = 0.0;
    }

    void step() {
        const int N = static_cast<int>(cur.size()) - 1;
        for (int i = 1; i < N; ++i)                       // серце моделі
            next[i] = 2.0 * cur[i] - prev[i]
                    + r2 * (cur[i - 1] - 2.0 * cur[i] + cur[i + 1]);

        // закріплений край стоїть; вільний бачить за собою дзеркального сусіда: y[−1] = y[1]
        next[0] = (left  == End::Fixed) ? 0.0
                : 2.0 * cur[0] - prev[0] + 2.0 * r2 * (cur[1] - cur[0]);
        next[N] = (right == End::Fixed) ? 0.0
                : 2.0 * cur[N] - prev[N] + 2.0 * r2 * (cur[N - 1] - cur[N]);

        prev.swap(cur);      // ролі буферів по колу — жодного копіювання масивів
        cur.swap(next);
    }
};

int main() {
    const double c = 400.0, L = 0.65;      // швидкість хвилі (м/с) і довжина струни (м)
    const int    N = 200;                  // проміжків; вузлів N+1
    const double dx = L / N;               // 3.25 мм
    const double r  = 0.9;                 // число Куранта, r ≤ 1 (див. далі)
    const double dt = r * dx / c;          // 7.31 мкс

    StringSim s(N + 1, r, End::Fixed, End::Fixed);

    std::vector<double> y0(N + 1, 0.0), v0(N + 1, 0.0);   // відпускаємо без поштовху
    const double xp = 0.2 * L, h = 0.003;                 // защип: 1/5 довжини, висота 3 мм
    for (int i = 0; i <= N; ++i) {
        const double x = i * dx;
        y0[i] = (x < xp) ? h * x / xp : h * (L - x) / (L - xp);
    }
    s.start(y0, v0, dt);

    const int steps = static_cast<int>(0.01 / dt);        // 10 мс звучання
    for (int n = 0; n < steps; ++n) {
        s.step();
        std::printf("%.6f %+.6e\n", (n + 1) * dt, s.cur[N / 7]);   // «знімач» під струною
    }
    return 0;
}
