#include "statistics.hpp"

#include <algorithm>
#include <cmath>
#include <limits>
#include <numeric>
#include <ranges>

namespace stats {

double log_factorial(int n) {
    if (n <= 1) return 0.0;
    // Прямий добуток переповнить double уже на 171!, тому працюємо в логарифмах.
    return std::lgamma(static_cast<double>(n) + 1.0);
}

double fisher_exact(const Table& t) {
    const int n1 = t.a + t.b, n0 = t.c + t.d;
    const int m1 = t.a + t.c, m0 = t.b + t.d;
    const int total = n1 + n0;
    if (total <= 0 || n1 == 0 || n0 == 0 || m1 == 0 || m0 == 0) return 1.0;

    // Спільна частина гіпергеометричної ймовірності — рахуємо один раз.
    const double log_denom = log_factorial(n1) + log_factorial(n0) +
                             log_factorial(m1) + log_factorial(m0) - log_factorial(total);

    const double log_p_obs = log_denom - (log_factorial(t.a) + log_factorial(t.b) +
                                          log_factorial(t.c) + log_factorial(t.d));

    const int min_a = std::max(0, m1 - n0);
    const int max_a = std::min(n1, m1);

    // Двосторонній p — сума всіх розкладів, не ймовірніших за спостережений.
    double p_total = 0.0;
    for (int x = min_a; x <= max_a; ++x) {
        const int xb = n1 - x, xc = m1 - x, xd = n0 - xc;
        const double log_p = log_denom - (log_factorial(x) + log_factorial(xb) +
                                          log_factorial(xc) + log_factorial(xd));
        if (log_p <= log_p_obs + 1e-9) p_total += std::exp(log_p);
    }
    return std::clamp(p_total, 0.0, 1.0);
}

Effect effect_size(const Table& t) {
    Effect e;
    double a = t.a, b = t.b, c = t.c, d = t.d;

    // Корекція Холдейна — Енскомба: без неї порожня клітинка дає OR = +inf.
    if (a == 0.0 || b == 0.0 || c == 0.0 || d == 0.0) {
        a += 0.5; b += 0.5; c += 0.5; d += 0.5;
        e.haldane = true;
    }
    e.odds_ratio = (a * d) / (b * c);

    const double se = std::sqrt(1.0 / a + 1.0 / b + 1.0 / c + 1.0 / d);
    const double ln_or = std::log(e.odds_ratio);
    e.ci_low = std::exp(ln_or - 1.96 * se);
    e.ci_high = std::exp(ln_or + 1.96 * se);
    return e;
}

double chi2_tail_1df(double chi2) {
    if (!(chi2 > 0.0)) return 1.0;
    return std::erfc(std::sqrt(chi2 / 2.0));   // хвіст χ² з одним ступенем свободи
}

std::vector<double> benjamini_hochberg(std::span<const double> p) {
    std::vector<double> adjusted(p.size(), 1.0);
    if (p.empty()) return adjusted;

    std::vector<std::size_t> order(p.size());
    std::iota(order.begin(), order.end(), std::size_t{0});
    std::ranges::sort(order, {}, [&](std::size_t i) { return p[i]; });

    // Ідемо від найбільшого p донизу, тримаючи монотонність.
    double previous = 1.0;
    const auto n = static_cast<double>(p.size());
    for (std::size_t k = order.size(); k-- > 0;) {
        double q = p[order[k]] * n / static_cast<double>(k + 1);
        q = std::min({q, previous, 1.0});
        previous = q;
        adjusted[order[k]] = q;
    }
    return adjusted;
}

Stratified mantel_haenszel(std::span<const Table> strata) {
    Stratified r;
    double num = 0.0, den = 0.0, sum_a = 0.0, sum_e = 0.0, sum_v = 0.0;

    for (const auto& t : strata) {
        const double a = t.a, b = t.b, c = t.c, d = t.d;
        const double N = a + b + c + d;
        if (N <= 1.0) continue;
        const double n1 = a + b, n0 = c + d, m1 = a + c, m0 = b + d;
        if (n1 == 0.0 || n0 == 0.0 || m1 == 0.0 || m0 == 0.0) continue;   // страта без інформації

        num += a * d / N;
        den += b * c / N;
        sum_a += a;
        sum_e += n1 * m1 / N;
        sum_v += n1 * n0 * m1 * m0 / (N * N * (N - 1.0));
        ++r.strata;
    }
    if (r.strata == 0) {
        r.odds_ratio = std::numeric_limits<double>::quiet_NaN();
        r.p_value = std::numeric_limits<double>::quiet_NaN();
        return r;
    }

    if (den > 0.0) r.odds_ratio = num / den;
    else if (num > 0.0) r.odds_ratio = std::numeric_limits<double>::infinity();
    else r.odds_ratio = std::numeric_limits<double>::quiet_NaN();

    if (sum_v > 0.0) {
        const double dev = std::max(0.0, std::fabs(sum_a - sum_e) - 0.5);   // поправка на неперервність
        r.chi2 = dev * dev / sum_v;
        r.p_value = chi2_tail_1df(r.chi2);
    } else {
        r.p_value = 1.0;
    }
    return r;
}

}  // namespace stats
