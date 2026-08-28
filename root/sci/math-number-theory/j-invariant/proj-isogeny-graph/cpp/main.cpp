#include <iostream>
#include <vector>
#include <unordered_set>
#include <queue>
#include <optional>
#include <cstdint>
#include <span>

namespace jinv {

constexpr int64_t P_PRIME = 431;

/* Модульне кільце Z_p */
constexpr int64_t mod_p(int64_t a) noexcept {
    int64_t r = a % P_PRIME;
    return r < 0 ? r + P_PRIME : r;
}

constexpr int64_t exp_mod(int64_t base, int64_t exp) noexcept {
    int64_t res = 1;
    base = mod_p(base);
    while (exp > 0) {
        if (exp & 1) res = mod_p(res * base);
        base = mod_p(base * base);
        exp >>= 1;
    }
    return res;
}

constexpr int64_t inv_mod(int64_t a) noexcept {
    return exp_mod(a, P_PRIME - 2);
}

/* Типобезпечне поле F_{p^2} */
struct Fp2 {
    int64_t re{0};
    int64_t im{0};

    constexpr Fp2() noexcept = default;
    constexpr Fp2(int64_t r, int64_t i = 0) noexcept : re(mod_p(r)), im(mod_p(i)) {}

    constexpr bool operator==(const Fp2& o) const noexcept {
        return re == o.re && im == o.im;
    }

    constexpr Fp2 operator+(const Fp2& o) const noexcept {
        return { re + o.re, im + o.im };
    }

    constexpr Fp2 operator-(const Fp2& o) const noexcept {
        return { re - o.re, im - o.im };
    }

    constexpr Fp2 operator*(const Fp2& o) const noexcept {
        return { re * o.re - im * o.im, re * o.im + im * o.re };
    }

    constexpr Fp2 inv() const noexcept {
        int64_t norm = mod_p(re * re + im * im);
        int64_t inv_n = inv_mod(norm);
        return { re * inv_n, -im * inv_n };
    }
};

/* Хеш-функція для збереження у std::unordered_set */
struct Fp2Hash {
    std::size_t operator()(const Fp2& k) const noexcept {
        return std::hash<int64_t>()(k.re) ^ (std::hash<int64_t>()(k.im) << 16);
    }
};

/* Еліптична крива: y^2 = x^3 + Ax + B */
class EllipticCurve {
public:
    Fp2 a;
    Fp2 b;

    constexpr EllipticCurve(Fp2 a_val, Fp2 b_val) noexcept : a(a_val), b(b_val) {}

    /* Обчислення j-інваріанта з перевіркою дискримінанта */
    [[nodiscard]] std::optional<Fp2> j_invariant() const noexcept {
        Fp2 a3 = a * a * a;
        Fp2 b2 = b * b;
        Fp2 four(4);
        Fp2 twenty_seven(27);
        Fp2 c1728(1728);

        Fp2 num = c1728 * (four * a3);
        Fp2 den = (four * a3) + (twenty_seven * b2);

        if (den.re == 0 && den.im == 0) {
            return std::nullopt; // Сингулярна крива
        }
        return num * den.inv();
    }

    /* Відновлення кривої за інваріантом j0 */
    [[nodiscard]] static EllipticCurve from_j(Fp2 j0) noexcept {
        Fp2 c1728(1728);
        Fp2 zero(0);

        if (j0 == zero) {
            return EllipticCurve(zero, Fp2(1)); // y^2 = x^3 + 1
        }
        if (j0 == c1728) {
            return EllipticCurve(Fp2(1), zero); // y^2 = x^3 + x
        }

        Fp2 diff = c1728 - j0;
        Fp2 j_diff = j0 * diff;
        Fp2 a_res = Fp2(3) * j_diff;
        Fp2 b_res = Fp2(2) * j_diff * diff;
        return EllipticCurve(a_res, b_res);
    }
};

/* Модулярний поліном 2-ізогеній */
[[nodiscard]] Fp2 eval_modular_poly2(Fp2 X, Fp2 Y) noexcept {
    Fp2 X2 = X * X, X3 = X2 * X;
    Fp2 Y2 = Y * Y, Y3 = Y2 * Y;

    Fp2 term1 = (X3 + Y3) - (X2 * Y2);
    Fp2 term2 = Fp2(1488) * (X2 * Y + X * Y2);
    Fp2 term3 = Fp2(162000) * (X2 + Y2);
    Fp2 term4 = Fp2(40773375) * (X * Y);
    Fp2 term5 = Fp2(mod_p(8748000000LL)) * (X + Y);
    Fp2 term6 = Fp2(mod_p(157464000000000LL));

    return term1 + term2 - term3 + term4 + term5 - term6;
}

/* Дослідник графа ізогеній через BFS */
class IsogenyGraphExplorer {
public:
    static std::vector<Fp2> find_neighbors(Fp2 j_curr) {
        std::vector<Fp2> neighbors;
        for (int64_t re = 0; re < P_PRIME; ++re) {
            for (int64_t im = 0; im < P_PRIME; ++im) {
                Fp2 cand(re, im);
                if (eval_modular_poly2(j_curr, cand) == Fp2(0, 0)) {
                    neighbors.push_back(cand);
                }
            }
        }
        return neighbors;
    }

    static std::unordered_set<Fp2, Fp2Hash> explore_component(Fp2 start_j, size_t max_nodes = 50) {
        std::unordered_set<Fp2, Fp2Hash> visited;
        std::queue<Fp2> q;

        q.push(start_j);
        visited.insert(start_j);

        while (!q.empty() && visited.size() < max_nodes) {
            Fp2 u = q.front();
            q.pop();

            for (const auto& v : find_neighbors(u)) {
                if (!visited.contains(v)) {
                    visited.insert(v);
                    q.push(v);
                }
            }
        }
        return visited;
    }
};

} // namespace jinv

int main() {
    std::cout << "=== Обхід графа ізогеній еліптичних кривих (C++20) ===\n";
    std::cout << "Поле: F_p, p = " << jinv::P_PRIME << "\n\n";

    using namespace jinv;

    // 1. Тест класифікації кривих
    EllipticCurve c1(Fp2(0), Fp2(1));
    if (auto j = c1.j_invariant()) {
        std::cout << "Крива y^2 = x^3 + 1: j = (" << j->re << " + " << j->im << "i) [Очікується: 0]\n";
    }

    EllipticCurve c2(Fp2(1), Fp2(0));
    if (auto j = c2.j_invariant()) {
        std::cout << "Крива y^2 = x^3 + x: j = (" << j->re << " + " << j->im << "i) [Очікується: " << mod_p(1728) << "]\n";
    }

    // 2. Відновлення та перевірка інваріанта
    Fp2 target_j(123, 0);
    auto recon = EllipticCurve::from_j(target_j);
    auto recon_j = recon.j_invariant();
    std::cout << "Відновлено для j=123: A=" << recon.a.re << ", B=" << recon.b.re
              << " -> j(E)=" << recon_j->re << "\n";

    // 3. Пошук сусідів у графі Рамануджана
    auto neighbors = IsogenyGraphExplorer::find_neighbors(Fp2(1728));
    std::cout << "\nЗнайдено 2-ізогенних сусідів для j=1728: " << neighbors.size() << "\n";
    for (size_t i = 0; i < neighbors.size(); ++i) {
        std::cout << "  [" << i + 1 << "] j = (" << neighbors[i].re << " + " << neighbors[i].im << "i)\n";
    }

    return 0;
}
