#include <iostream>
#include <vector>
#include <iomanip>
#include <cmath>
#include <cstdint>
#include <string>

struct EllipticCurve11 {
    int64_t a1 = 0;
    int64_t a2 = -1;
    int64_t a3 = 1;
    int64_t a4 = -10;
    int64_t a6 = -20;

    int64_t countPointsModP(int64_t p) const {
        if (p == 2) {
            int64_t count = 1; // нескінченно віддалена точка O
            for (int64_t x = 0; x < 2; ++x) {
                for (int64_t y = 0; y < 2; ++y) {
                    int64_t lhs = (y * y + a1 * x * y + a3 * y) % 2;
                    int64_t rhs = (x * x * x + a2 * x * x + a4 * x + a6) % 2;
                    if ((lhs - rhs) % 2 == 0) ++count;
                }
            }
            return count;
        }

        int64_t b2 = ((a1 * a1 + 4 * a2) % p + p) % p;
        int64_t b4 = ((a1 * a3 + 2 * a4) % p + p) % p;
        int64_t b6 = ((a3 * a3 + 4 * a6) % p + p) % p;

        std::vector<int64_t> sq_roots(p, 0);
        for (int64_t y = 0; y < p; ++y) {
            int64_t y2 = (y * y) % p;
            sq_roots[y2]++;
        }

        int64_t count = 1; // точка O
        for (int64_t x = 0; x < p; ++x) {
            int64_t rhs = (4 * x % p * x % p * x + b2 * x % p * x + 2 * b4 * x + b6) % p;
            rhs = (rhs + p) % p;
            count += sq_roots[rhs];
        }
        return count;
    }
};

std::vector<int64_t> expandModularForm(int64_t max_n) {
    std::vector<int64_t> poly(max_n + 1, 0);
    poly[0] = 1;

    auto applyFactor = [&](int64_t shift) {
        std::vector<int64_t> next_p = poly;
        for (int64_t i = shift; i <= max_n; ++i) {
            next_p[i] -= poly[i - shift];
        }
        poly = std::move(next_p);
    };

    for (int64_t n = 1; n <= max_n; ++n) {
        applyFactor(n);
        applyFactor(n);
    }
    for (int64_t n = 1; n * 11 <= max_n; ++n) {
        applyFactor(11 * n);
        applyFactor(11 * n);
    }

    std::vector<int64_t> coeffs(max_n + 1, 0);
    for (int64_t n = 1; n <= max_n; ++n) {
        coeffs[n] = poly[n - 1];
    }
    return coeffs;
}

bool isPrime(int64_t n) {
    if (n < 2) return false;
    for (int64_t d = 2; d * d <= n; ++d) {
        if (n % d == 0) return false;
    }
    return true;
}

int main() {
    EllipticCurve11 curve;
    const int64_t max_p = 50;
    auto q_coeffs = expandModularForm(max_p);

    std::cout << std::left 
              << std::setw(10) << "Просте p"
              << std::setw(14) << "#E(F_p)"
              << std::setw(16) << "Слід a_p(E)"
              << std::setw(16) << "Коеф. a_p(f)"
              << std::setw(10) << "Збіг?" << "\n";
    std::cout << std::string(66, '-') << "\n";

    for (int64_t p = 2; p <= max_p; ++p) {
        if (!isPrime(p)) continue;

        int64_t ap_curve = 0;
        std::string pts_str;
        if (p == 11) {
            ap_curve = -1; // погана редукція
            pts_str = "погана ред.";
        } else {
            int64_t pts = curve.countPointsModP(p);
            ap_curve = p + 1 - pts;
            pts_str = std::to_string(pts);
        }

        int64_t ap_form = q_coeffs[p];
        std::string match = (ap_curve == ap_form) ? "✓ ТАК" : "✗ НІ";

        std::cout << std::left
                  << std::setw(10) << p
                  << std::setw(14) << pts_str
                  << std::setw(16) << ap_curve
                  << std::setw(16) << ap_form
                  << std::setw(10) << match << "\n";
    }

    return 0;
}
