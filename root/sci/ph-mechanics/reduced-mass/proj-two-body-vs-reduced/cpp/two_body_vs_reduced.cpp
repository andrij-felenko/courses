// two_body_vs_reduced.cpp
// g++ -O2 -std=c++17 two_body_vs_reduced.cpp -o twobody
#include <algorithm>
#include <cmath>
#include <complex>
#include <cstdio>

using Vec    = std::complex<double>;   // 2D-вектор: різниця й множення на скаляр уже є
using Force  = Vec (*)(Vec);
using Energy = double (*)(double);
using Exact  = Vec (*)(double);

struct Pair {                          // чесна пара: два тіла, дві сили
    double m1, m2;
    Vec r1, r2, v1, v2, a1, a2, g;
    Force force;

    Pair(double m1_, double m2_, Vec r1_, Vec r2_, Vec v1_, Vec v2_, Force f, Vec g_ = {})
        : m1(m1_), m2(m2_), r1(r1_), r2(r2_), v1(v1_), v2(v2_), g(g_), force(f) { accel(); }

    void accel() {
        const Vec F = force(r1 - r2);          // сила на тіло 1 з боку тіла 2
        a1 =  F / m1 + g;
        a2 = -F / m2 + g;                      // третій закон: рівно й назустріч
    }
    void step(double h) {                      // швидкісний Верле
        v1 += 0.5 * h * a1;   v2 += 0.5 * h * a2;
        r1 += h * v1;         r2 += h * v2;
        accel();
        v1 += 0.5 * h * a1;   v2 += 0.5 * h * a2;
    }
    Vec r() const { return r1 - r2; }
};

struct Reduced {                       // одна уявна частинка маси mu у точці r
    double mu;
    Vec r, v, a;
    Force force;

    Reduced(double mu_, Vec r_, Vec v_, Force f)
        : mu(mu_), r(r_), v(v_), force(f) { a = force(r) / mu; }

    void step(double h) {
        v += 0.5 * h * a;
        r += h * v;
        a = force(r) / mu;
        v += 0.5 * h * a;
    }
};

void compare(const char* name, double m1, double m2, Vec r0, Vec v0,
             Force force, Energy energy, double h, long steps, const char* unit,
             Vec R0 = {}, Vec V0 = {}, Vec g = {}, Exact exact = nullptr)
{
    const double M = m1 + m2, mu = m1 * m2 / M;
    Pair pair(m1, m2,
              R0 + (m2 / M) * r0, R0 - (m1 / M) * r0,      // r₁ = R + (m₂/M)·r
              V0 + (m2 / M) * v0, V0 - (m1 / M) * v0,      // r₂ = R − (m₁/M)·r
              force, g);
    Reduced red(mu, r0, v0, force);

    const double E0 = 0.5 * mu * std::norm(v0) + energy(std::abs(r0));
    const long mark = std::max(1L, steps / 4);
    double scale = std::abs(r0), dRel = 0, dBody = 0, dE = 0, dExact = 0;
    double gt[4] = {}, gd[4] = {};
    int gn = 0;

    for (long n = 1; n <= steps; ++n) {
        pair.step(h);
        red.step(h);
        const double t = n * h;
        dRel = std::max(dRel, std::abs(pair.r() - red.r));
        // відновлення справжнього тіла 1: зведений розв'язок + рух центра мас
        const Vec Rt = R0 + V0 * t + 0.5 * g * (t * t);
        dBody = std::max(dBody, std::abs(Rt + (m2 / M) * red.r - pair.r1));
        const double E = 0.5 * mu * std::norm(red.v) + energy(std::abs(red.r));
        dE = std::max(dE, std::fabs(E - E0));
        scale = std::max(scale, std::abs(red.r));
        if (exact) dExact = std::max(dExact, std::abs(red.r - exact(t)));
        if (n % mark == 0 && gn < 4) { gt[gn] = t; gd[gn] = dRel; ++gn; }
    }

    std::printf("[%s]  h=%g, кроків=%ld, μ=%.6g\n", name, h, steps, mu);
    std::printf("  розбіжність двох способів  max|Δr| = %.3e %s  (%.1e від масштабу)\n",
                dRel, unit, dRel / scale);
    std::printf("  відновлене тіло 1 проти чесного    = %.3e %s\n", dBody, unit);
    std::printf("  власна похибка Верле (розмах по енергії) = %.2e відносних\n", std::fabs(dE / E0));
    if (exact)
        std::printf("  зведений прогін проти точного ω = √(k/μ) = %.3e %s\n", dExact, unit);
    std::printf("  як росте |Δr|: ");
    for (int i = 0; i < gn; ++i) std::printf("  %.3g→%.1e", gt[i], gd[i]);
    std::printf("\n\n");
}

constexpr double PI = 3.14159265358979323846;

// ── 1. Сонце + Юпітер: AU, рік, маса Сонця; G = 4π² ─────────────────────────
constexpr double G  = 4.0 * PI * PI;
constexpr double mS = 1.0, mJ = 9.5479e-4;      // M☉/M♃ = 1047.35
constexpr double aJ = 5.2038, eJ = 0.0489;      // велика піввісь і ексцентриситет

Vec kepler(Vec r) {
    const double d = std::abs(r);
    return (-G * mS * mJ / (d * d * d)) * r;
}
double kepler_U(double d) { return -G * mS * mJ / d; }

// ── 2. Два вантажі на пружині: СІ ───────────────────────────────────────────
constexpr double m1s = 0.4, m2s = 1.1, kSpr = 30.0, L0 = 0.25, A0 = 0.05;
const double wSpr = std::sqrt(kSpr * (m1s + m2s) / (m1s * m2s));   // ω = √(k/μ)

Vec spring(Vec r) {
    const double d = std::abs(r);
    return (-kSpr * (d - L0) / d) * r;
}
double spring_U(double d) { return 0.5 * kSpr * (d - L0) * (d - L0); }
Vec spring_exact(double t) { return Vec(L0 + A0 * std::cos(wSpr * t), 0.0); }

int main() {
    const double T = 2 * PI * std::sqrt(aJ * aJ * aJ / (G * (mS + mJ)));
    std::printf("період з формули = %.4f року (таблиця: 11.862)\n\n", T);

    const Vec  r0(aJ * (1 + eJ), 0.0);          // старт в афелії
    const Vec  v0(0.0, std::sqrt(G * (mS + mJ) / aJ * (1 - eJ) / (1 + eJ)));
    const double h = 1e-3;
    const long   N = static_cast<long>(10 * T / h);

    compare("Кеплер: Сонце + Юпітер, 10 обертів", mJ, mS, r0, v0, kepler, kepler_U,
            h, N, "AU", Vec(0.3, -0.7), Vec(0.11, 0.05));
    compare("Те саме + стороннє однорідне поле (лише в чесному прогоні)", mJ, mS, r0, v0,
            kepler, kepler_U, h, N, "AU", Vec(0.3, -0.7), Vec(0.11, 0.05), Vec(0.02, -0.01));

    compare("Пружина: проти точного ω = √(k/μ), 20 періодів", m1s, m2s,
            Vec(L0 + A0, 0.0), Vec(), spring, spring_U,
            1e-5, static_cast<long>(20 * 2 * PI / wSpr / 1e-5), "м",
            Vec(0.0, 0.1), Vec(1.5, 0.0), Vec(), spring_exact);

    // ── 3. Витягнута орбіта: той самий крок уже нікуди не годиться ──────────
    for (double hh : {1e-3, 1e-5}) {
        const double e2 = 0.95;
        char name[96];
        std::snprintf(name, sizeof name, "Кеплер e=0.95, 3 оберти, h=%g", hh);
        compare(name, mJ, mS, Vec(aJ * (1 + e2), 0.0),
                Vec(0.0, std::sqrt(G * (mS + mJ) / aJ * (1 - e2) / (1 + e2))),
                kepler, kepler_U, hh, static_cast<long>(3 * T / hh), "AU");
    }
    return 0;
}
