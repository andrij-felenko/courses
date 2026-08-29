#include <iostream>
#include <vector>
#include <complex>
#include <numeric>
#include <cmath>
#include <optional>
#include <iomanip>
#include <string>
#include <algorithm>

class DirichletCharacterTable {
public:
    using Complex = std::complex<double>;

    struct CharacterInfo {
        int index;
        int conductor;
        bool is_primitive;
        bool is_even;
        bool is_real;
    };

    explicit DirichletCharacterTable(int modulus) : q_(modulus) {
        build_coprimes();
        g_ = find_primitive_root();
        if (g_.has_value()) {
            build_table_cyclic();
        }
    }

    [[nodiscard]] int modulus() const noexcept { return q_; }
    [[nodiscard]] int phi() const noexcept { return static_cast<int>(coprimes_.size()); }
    [[nodiscard]] const std::vector<int>& coprimes() const noexcept { return coprimes_; }
    [[nodiscard]] std::optional<int> primitive_root() const noexcept { return g_; }

    [[nodiscard]] Complex eval(int char_idx, int n) const {
        int rem = ((n % q_) + q_) % q_;
        if (std::gcd(rem, q_) != 1) return {0.0, 0.0};
        auto it = std::find(coprimes_.begin(), coprimes_.end(), rem);
        if (it == coprimes_.end()) return {0.0, 0.0};
        auto elem_idx = static_cast<size_t>(std::distance(coprimes_.begin(), it));
        return table_[char_idx][elem_idx];
    }

    [[nodiscard]] int compute_conductor(int char_idx) const {
        constexpr double kEps = 1e-6;
        for (int d = 1; d <= q_; ++d) {
            if (q_ % d != 0) continue;
            bool is_cond = true;
            for (size_t i = 0; i < coprimes_.size(); ++i) {
                if (coprimes_[i] % d == 1 % d) {
                    if (std::abs(table_[char_idx][i] - Complex{1.0, 0.0}) > kEps) {
                        is_cond = false;
                        break;
                    }
                }
            }
            if (is_cond) return d;
        }
        return q_;
    }

    [[nodiscard]] bool is_even(int char_idx) const {
        int minus_one = q_ - 1;
        Complex val = eval(char_idx, minus_one);
        return val.real() > 0.0;
    }

    [[nodiscard]] bool is_real(int char_idx) const {
        constexpr double kEps = 1e-6;
        for (size_t i = 0; i < coprimes_.size(); ++i) {
            if (std::abs(table_[char_idx][i].imag()) > kEps) return false;
        }
        return true;
    }

    [[nodiscard]] CharacterInfo character_info(int char_idx) const {
        int cond = compute_conductor(char_idx);
        return CharacterInfo{
            char_idx,
            cond,
            cond == q_,
            is_even(char_idx),
            is_real(char_idx)
        };
    }

    [[nodiscard]] Complex row_scalar_product(int char_a, int char_b) const {
        Complex sum{0.0, 0.0};
        for (size_t i = 0; i < coprimes_.size(); ++i) {
            sum += table_[char_a][i] * std::conj(table_[char_b][i]);
        }
        return sum;
    }

    [[nodiscard]] Complex col_scalar_product(int elem_m, int elem_n) const {
        Complex sum{0.0, 0.0};
        for (int k = 0; k < phi(); ++k) {
            sum += eval(k, elem_m) * std::conj(eval(k, elem_n));
        }
        return sum;
    }

    [[nodiscard]] Complex fourier_delta_filter(int a, int n) const {
        Complex sum{0.0, 0.0};
        for (int k = 0; k < phi(); ++k) {
            sum += std::conj(eval(k, a)) * eval(k, n);
        }
        return sum / static_cast<double>(phi());
    }

    void print_summary() const {
        std::cout << "Таблиця характерів Діріхле (mod " << q_ << "), φ(q) = " << phi() << ":\n";
        std::cout << "----------------------------------------------------------------------\n";
        for (int k = 0; k < phi(); ++k) {
            CharacterInfo info = character_info(k);
            std::cout << "χ_" << k << " [cond=" << info.conductor << ", "
                      << (info.is_primitive ? "первісний" : "індукований") << ", "
                      << (info.is_even ? "парний" : "непарний") << ", "
                      << (info.is_real ? "дійсний" : "комплексний") << "]:\n  ";
            for (size_t i = 0; i < coprimes_.size(); ++i) {
                std::cout << "n=" << coprimes_[i] << ":("
                          << std::fixed << std::setprecision(2)
                          << std::showpos << table_[k][i].real()
                          << table_[k][i].imag() << "i) "
                          << std::noshowpos;
            }
            std::cout << "\n";
        }
    }

    void verify_orthogonality() const {
        std::cout << "\n--- Перевірка співвідношень ортогональності (mod " << q_ << ") ---\n";
        constexpr double kEps = 1e-5;

        /* Перша ортогональність: рядки */
        bool row_ok = true;
        for (int a = 0; a < phi(); ++a) {
            for (int b = 0; b < phi(); ++b) {
                Complex dot = row_scalar_product(a, b);
                double expected = (a == b) ? static_cast<double>(phi()) : 0.0;
                if (std::abs(dot - Complex{expected, 0.0}) > kEps) row_ok = false;
            }
        }
        std::cout << "1. Ортогональність за рядками (елементами групи): "
                  << (row_ok ? "ПІДТВЕРДЖЕНО" : "ПОМИЛКА") << "\n";

        /* Друга ортогональність: стовпчики */
        bool col_ok = true;
        for (int m : coprimes_) {
            for (int n : coprimes_) {
                Complex dot = col_scalar_product(m, n);
                double expected = (m == n) ? static_cast<double>(phi()) : 0.0;
                if (std::abs(dot - Complex{expected, 0.0}) > kEps) col_ok = false;
            }
        }
        std::cout << "2. Ортогональність за стовпчиками (характерами):   "
                  << (col_ok ? "ПІДТВЕРДЖЕНО" : "ПОМИЛКА") << "\n";
    }

private:
    int q_;
    std::vector<int> coprimes_;
    std::optional<int> g_;
    std::vector<std::vector<Complex>> table_;

    void build_coprimes() {
        for (int i = 1; i < q_; ++i) {
            if (std::gcd(i, q_) == 1) coprimes_.push_back(i);
        }
    }

    [[nodiscard]] std::optional<int> find_primitive_root() const {
        if (q_ == 2) return 1;
        int phi_val = phi();
        for (int g = 2; g < q_; ++g) {
            if (std::gcd(g, q_) != 1) continue;
            bool ok = true;
            int temp = phi_val;
            for (int p = 2; p * p <= temp; ++p) {
                if (temp % p == 0) {
                    if (power_mod(g, phi_val / p, q_) == 1) { ok = false; break; }
                    while (temp % p == 0) temp /= p;
                }
            }
            if (temp > 1 && ok && power_mod(g, phi_val / temp, q_) == 1) ok = false;
            if (ok) return g;
        }
        return std::nullopt;
    }

    static int power_mod(int base, int exp, int mod) {
        int res = 1;
        base %= mod;
        while (exp > 0) {
            if (exp % 2 == 1) res = (res * base) % mod;
            base = (base * base) % mod;
            exp /= 2;
        }
        return res;
    }

    void build_table_cyclic() {
        int phi_val = phi();
        std::vector<int> discrete_log(q_, 0);
        int curr = 1;
        for (int exp = 0; exp < phi_val; ++exp) {
            discrete_log[curr] = exp;
            curr = (curr * (*g_)) % q_;
        }

        constexpr double kPi = 3.14159265358979323846;
        table_.assign(phi_val, std::vector<Complex>(phi_val));
        for (int k = 0; k < phi_val; ++k) {
            for (size_t i = 0; i < coprimes_.size(); ++i) {
                int n = coprimes_[i];
                int idx = discrete_log[n];
                double angle = 2.0 * kPi * k * idx / phi_val;
                table_[k][i] = std::polar(1.0, angle);
            }
        }
    }
};

int main() {
    DirichletCharacterTable table(5);
    table.print_summary();
    table.verify_orthogonality();

    std::cout << "\n--- Спектральне відновлення дельта-фільтра δ(n ≡ 3 mod 5) ---\n";
    for (int n : table.coprimes()) {
        auto delta = table.fourier_delta_filter(3, n);
        std::cout << "δ(" << n << " ≡ 3 mod 5) = "
                  << std::fixed << std::setprecision(2) << delta.real() << "\n";
    }

    return 0;
}

