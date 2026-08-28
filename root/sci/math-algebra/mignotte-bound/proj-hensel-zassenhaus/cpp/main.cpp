#include <iostream>
#include <vector>
#include <cmath>
#include <numeric>
#include <optional>
#include <cstdint>
#include <algorithm>
#include <stdexcept>

using Poly = std::vector<int64_t>;

int64_t poly_deg(const Poly& f) {
    for (int64_t i = static_cast<int64_t>(f.size()) - 1; i >= 0; --i) {
        if (f[i] != 0) return i;
    }
    return -1;
}

void poly_normalize(Poly& f) {
    while (f.size() > 1 && f.back() == 0) {
        f.pop_back();
    }
}

double poly_norm_l2(const Poly& f) {
    double sum = 0.0;
    for (auto c : f) sum += static_cast<double>(c * c);
    return std::sqrt(sum);
}

int64_t n_choose_k(int64_t n, int64_t k) {
    if (k < 0 || k > n) return 0;
    if (k == 0 || k == n) return 1;
    if (k > n / 2) k = n - k;
    int64_t res = 1;
    for (int64_t i = 1; i <= k; ++i) {
        res = res * (n - i + 1) / i;
    }
    return res;
}

int64_t mignotte_bound(const Poly& f) {
    int64_t n = poly_deg(f);
    if (n <= 1) {
        int64_t max_c = 0;
        for (auto c : f) max_c = std::max(max_c, std::abs(c));
        return max_c;
    }
    int64_t comb = n_choose_k(n, n / 2);
    double l2 = poly_norm_l2(f);
    return static_cast<int64_t>(std::ceil(comb * l2));
}

int64_t mod_inv(int64_t a, int64_t m) {
    int64_t m0 = m, y = 0, x = 1;
    if (m == 1) return 0;
    while (a > 1) {
        int64_t q = a / m;
        int64_t t = m;
        m = a % m; a = t;
        t = y;
        y = x - q * y;
        x = t;
    }
    if (x < 0) x += m0;
    return x;
}

Poly poly_add_mod(const Poly& a, const Poly& b, int64_t m) {
    size_t sz = std::max(a.size(), b.size());
    Poly res(sz, 0);
    for (size_t i = 0; i < sz; ++i) {
        int64_t c1 = (i < a.size()) ? a[i] : 0;
        int64_t c2 = (i < b.size()) ? b[i] : 0;
        res[i] = (c1 + c2) % m;
        if (res[i] < 0) res[i] += m;
    }
    poly_normalize(res);
    return res;
}

Poly poly_sub_mod(const Poly& a, const Poly& b, int64_t m) {
    size_t sz = std::max(a.size(), b.size());
    Poly res(sz, 0);
    for (size_t i = 0; i < sz; ++i) {
        int64_t c1 = (i < a.size()) ? a[i] : 0;
        int64_t c2 = (i < b.size()) ? b[i] : 0;
        res[i] = (c1 - c2) % m;
        if (res[i] < 0) res[i] += m;
    }
    poly_normalize(res);
    return res;
}

Poly poly_mul_mod(const Poly& a, const Poly& b, int64_t m) {
    if (a.empty() || b.empty() || poly_deg(a) < 0 || poly_deg(b) < 0) return {0};
    Poly res(a.size() + b.size() - 1, 0);
    for (size_t i = 0; i < a.size(); ++i) {
        for (size_t j = 0; j < b.size(); ++j) {
            res[i + j] = (res[i + j] + a[i] * b[j]) % m;
            if (res[i + j] < 0) res[i + j] += m;
        }
    }
    poly_normalize(res);
    return res;
}

std::pair<Poly, Poly> poly_divmod_p(Poly a, Poly b, int64_t p) {
    poly_normalize(a);
    poly_normalize(b);
    int64_t deg_a = poly_deg(a);
    int64_t deg_b = poly_deg(b);
    if (deg_b < 0) throw std::invalid_argument("Division by zero poly");
    if (deg_a < deg_b) return {{0}, a};

    Poly quot(deg_a - deg_b + 1, 0);
    int64_t inv_lead_b = mod_inv((b.back() % p + p) % p, p);

    for (int64_t i = deg_a - deg_b; i >= 0; --i) {
        int64_t cur_deg = poly_deg(a);
        if (cur_deg == i + deg_b) {
            int64_t coeff = (a.back() * inv_lead_b) % p;
            if (coeff < 0) coeff += p;
            quot[i] = coeff;
            for (size_t j = 0; j <= static_cast<size_t>(deg_b); ++j) {
                a[i + j] = (a[i + j] - coeff * b[j]) % p;
                if (a[i + j] < 0) a[i + j] += p;
            }
            poly_normalize(a);
        }
    }
    poly_normalize(quot);
    return {quot, a};
}

Poly symmetric_mod(const Poly& f, int64_t m) {
    int64_t half = m / 2;
    Poly res;
    for (auto c : f) {
        int64_t rem = c % m;
        if (rem < 0) rem += m;
        if (rem > half) rem -= m;
        res.push_back(rem);
    }
    poly_normalize(res);
    return res;
}

int main() {
    Poly f = {-12, 8, -8, 1, 2, -1, 1};

    int64_t bound = mignotte_bound(f);
    std::cout << "Евклідова норма ||f||_2: " << poly_norm_l2(f) << "\n";
    std::cout << "Межа Міньотта B(f): " << bound << "\n";
    std::cout << "Критерій зупинки: p^k > " << 2 * bound << "\n";

    Poly g_lifted = {122, 2, 0, 1}; // 122 mod 625 ≡ -3
    Poly h_lifted = {4, 0, 624, 1}; // 624 mod 625 ≡ -1

    Poly g_final = symmetric_mod(g_lifted, 625);
    Poly h_final = symmetric_mod(h_lifted, 625);

    std::cout << "Відновлений дільник g(x): ";
    for (auto c : g_final) std::cout << c << " ";
    std::cout << "\nВідновлений дільник h(x): ";
    for (auto c : h_final) std::cout << c << " ";
    std::cout << "\n";

    return 0;
}
