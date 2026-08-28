#include <algorithm>
#include <cmath>
#include <cstdint>
#include <vector>

// Границі бінів — рівночастотні квантилі НАВЧАЛЬНОЇ вибірки.
// Порахували раз під час навчання, поклали в артефакт моделі й заморозили.
struct Binning {
    std::vector<double> edges;                       // внутрішні межі, зростаючі
    std::size_t bins() const { return edges.size() + 1; }
    std::size_t index(double x) const {              // O(log B) на значення
        return static_cast<std::size_t>(
            std::upper_bound(edges.begin(), edges.end(), x) - edges.begin());
    }
};

Binning fit_binning(std::vector<double> train, std::size_t B) {
    Binning b;
    if (train.empty() || B < 2) return b;
    std::sort(train.begin(), train.end());
    for (std::size_t i = 1; i < B; ++i)
        b.edges.push_back(train[train.size() * i / B]);
    // однакові межі означають порожній бін уже на навчанні — такий бін не потрібен
    b.edges.erase(std::unique(b.edges.begin(), b.edges.end()), b.edges.end());
    return b;
}

std::vector<std::uint64_t> histogram(const Binning& b, const std::vector<double>& xs) {
    std::vector<std::uint64_t> h(b.bins(), 0);
    for (double x : xs) ++h[b.index(x)];             // O(n log B) на весь потік
    return h;
}

// Частки з півдодаванням Джеффріса: (xᵢ + ½)/(N + B/2). Порожній бін перестає
// давати ln(0), а внесене зміщення спадає як 1/N.
std::vector<double> shares(const std::vector<std::uint64_t>& h) {
    const std::size_t B = h.size();
    double total = 0.0;
    for (std::uint64_t c : h) total += static_cast<double>(c);
    std::vector<double> p(B);
    for (std::size_t i = 0; i < B; ++i)
        p[i] = (static_cast<double>(h[i]) + 0.5)
             / (total + 0.5 * static_cast<double>(B));
    return p;
}

// PSI = Σ (pᵢ − qᵢ)·(ln pᵢ − ln qᵢ). O(B): уся робота вже зроблена в гістограмах.
double psi(const std::vector<double>& p, const std::vector<double>& q) {
    double s = 0.0;
    for (std::size_t i = 0; i < p.size(); ++i)
        s += (p[i] - q[i]) * (std::log(p[i]) - std::log(q[i]));
    return s;
}

// Межа тривоги замість сталих 0.10 і 0.25: (1/n + 1/m)·(B−1 + z_α·√(2(B−1))).
double psi_alarm(std::uint64_t n, std::uint64_t m, std::size_t B, double alpha) {
    const double df = static_cast<double>(B) - 1.0;
    return (1.0 / static_cast<double>(n) + 1.0 / static_cast<double>(m))
         * (df + z_for_tail(alpha) * std::sqrt(2.0 * df));
}
