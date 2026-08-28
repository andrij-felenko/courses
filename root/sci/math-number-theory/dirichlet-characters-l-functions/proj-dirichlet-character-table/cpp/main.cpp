#include <iostream>
#include <vector>
#include <complex>
#include <numeric>
#include <cmath>
#include <optional>
#include <iomanip>

class DirichletCharacterTable {
public:
    using Complex = std::complex<double>;

    explicit DirichletCharacterTable(int modulus) : q_(modulus) {
        build_coprimes();
        g_ = find_primitive_root();
        if (g_) {
            build_table_cyclic();
        }
    }

    [[nodiscard]] int modulus() const { return q_; }
    [[nodiscard]] int phi() const { return static_cast<int>(coprimes_.size()); }
    [[nodiscard]] const std::vector<int>& coprimes() const { return coprimes_; }

    [[nodiscard]] Complex eval(int char_idx, int n) const {
        int rem = ((n % q_) + q_) % q_;
        if (std::gcd(rem, q_) != 1) return {0.0, 0.0};
        auto it = std::find(coprimes_.begin(), coprimes_.end(), rem);
        size_t elem_idx = std::distance(coprimes_.begin(), it);
        return table_[char_idx][elem_idx];
    }

    [[nodiscard]] int compute_conductor(int char_idx) const {
        for (int d = 1; d <= q_; ++d) {
            if (q_ % d != 0) continue;
            bool is_cond = true;
            for (size_t i = 0; i < coprimes_.size(); ++i) {
                if (coprimes_[i] % d == 1 % d) {
                    if (std::abs(table_[char_idx][i] - Complex{1.0, 0.0}) > 1e-6) {
                        is_cond = false;
                        break;
                    }
                }
            }
            if (is_cond) return d;
        }
        return q_;
    }

    [[nodiscard]] Complex scalar_product(int char_a, int char_b) const {
        Complex sum{0.0, 0.0};
        for (size_t i = 0; i < coprimes_.size(); ++i) {
            sum += table_[char_a][i] * std::conj(table_[char_b][i]);
        }
        return sum;
    }

    void print_summary() const {
        std::cout << "Таблиця характерів (mod " << q_ << "), φ(q) = " << phi() << ":\n";
        for (int k = 0; k < phi(); ++k) {
            int cond = compute_conductor(k);
            std::cout << "χ_" << k << " [провідник d=" << cond << ", "
                      << (cond == q_ ? "первісний" : "індукований") << "]: ";
            for (size_t i = 0; i < coprimes_.size(); ++i) {
                std::cout << std::setw(6) << std::fixed << std::setprecision(2)
                          << table_[k][i] << " ";
            }
            std::cout << "\n";
        }
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

    std::optional<int> find_primitive_root() {
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

    auto prod = table.scalar_product(1, 2);
    std::cout << "\nПеревірка першої ортогональності <χ_1, χ_2> = " << prod << "\n";
    return 0;
}
