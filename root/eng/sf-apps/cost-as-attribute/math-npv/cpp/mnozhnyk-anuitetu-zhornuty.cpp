#include <cmath>
#include <vector>
#include <cstdio>

// Теперішня вартість суми fv, яку заплатять/отримають через n років.
double pv(double fv, double r, int n) { return fv / std::pow(1 + r, n); }

// flows[t] — потік у рік t (t = 0, 1, 2, …). Зводить усе до сьогодні.
double npv(const std::vector<double>& flows, double r) {
    double acc = 0.0;
    for (std::size_t t = 0; t < flows.size(); ++t)
        acc += flows[t] / std::pow(1 + r, static_cast<double>(t));
    return acc;
}

// A(r) = Σ 1/(1+r)^t за t = 1..n — замкнутий вигляд, без циклу.
double annuity_factor(double r, int n) {
    if (r == 0.0) return static_cast<double>(n);   // границя: дисконтувати нічого
    return (1 - std::pow(1 + r, -n)) / r;
}

int main() {
    // Рівний потік 60 тис. на рік п'ять років під 10 % — одним множенням:
    std::printf("%.2f\n", 60 * annuity_factor(0.10, 5));   // 227.45 тис.
}
