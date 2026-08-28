#include <iostream>
#include <vector>
#include <cmath>
#include <numeric>
#include <set>
#include <algorithm>

// Обчислення унікальних простих дільників
std::set<long long> get_prime_factors(long long n) {
    std::set<long long> factors;
    long long temp = std::abs(n);
    for (long long d = 2; d * d <= temp; ++d) {
        if (temp % d == 0) {
            factors.insert(d);
            while (temp % d == 0) {
                temp /= d;
            }
        }
    }
    if (temp > 1) {
        factors.insert(temp);
    }
    return factors;
}

// Обчислення радикала
long long compute_radical(long long n) {
    auto factors = get_prime_factors(n);
    long long rad = 1;
    for (auto p : factors) {
        rad *= p;
    }
    return rad;
}

struct CurveResult {
    long long a, b, c;
    long long rad;
    double sigma;
};

// Аналіз кривої Фрея для пари (a, b)
bool analyze_curve(long long a, long long b, CurveResult& out) {
    if (std::gcd(a, b) != 1) return false;
    long long c = a + b;
    long long abc = a * b * c;
    
    long long rad_abc = compute_radical(abc);
    long long conductor = rad_abc;
    if (abc % 2 != 0) conductor *= 2;
    
    // Дискримінант |Δ| = 16 * (abc)^2
    double log_disc = std::log(16.0) + 2.0 * std::log(std::abs((double)abc));
    double log_cond = std::log((double)conductor);
    
    out.a = a;
    out.b = b;
    out.c = c;
    out.rad = rad_abc;
    out.sigma = log_disc / log_cond;
    return true;
}

int main() {
    CurveResult res;
    if (analyze_curve(1, 4374, res)) {
        std::cout << "Frey Curve for 1 + 4374 = 4375:" << std::endl;
        std::cout << "  Radical rad(abc): " << res.rad << std::endl;
        std::cout << "  Szpiro Index sigma(E): " << res.sigma << std::endl;
    }
    return 0;
}
