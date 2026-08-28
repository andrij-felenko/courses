#include <iostream>
#include <vector>
#include <span>
#include <optional>
#include <algorithm>
#include <numeric>
#include <string>
#include <stdexcept>

/* Клас многочлена над скінченним полем F_p із семантикою значень */
class Polynomial {
private:
    int mod_;
    std::vector<int> coeffs_; /* coeffs_[i] - коефіцієнт при x^i */

    void normalize() {
        for (auto &c : coeffs_) {
            c = (c % mod_ + mod_) % mod_;
        }
        while (coeffs_.size() > 1 && coeffs_.back() == 0) {
            coeffs_.pop_back();
        }
    }

    static int mod_inverse(int a, int m) {
        a = (a % m + m) % m;
        int res = 1, base = a, exp = m - 2;
        while (exp > 0) {
            if (exp & 1) res = (res * base) % m;
            base = (base * base) % m;
            exp >>= 1;
        }
        return res;
    }

public:
    Polynomial(int mod = 2) : mod_(mod), coeffs_{0} {}
    Polynomial(std::initializer_list<int> list, int mod = 2) : mod_(mod), coeffs_(list) {
        normalize();
    }
    Polynomial(std::vector<int> coeffs, int mod = 2) : mod_(mod), coeffs_(std::move(coeffs)) {
        if (coeffs_.empty()) coeffs_.push_back(0);
        normalize();
    }

    [[nodiscard]] int degree() const noexcept {
        return static_cast<int>(coeffs_.size()) - 1;
    }

    [[nodiscard]] int mod() const noexcept { return mod_; }
    [[nodiscard]] int operator[](size_t i) const noexcept {
        return (i < coeffs_.size()) ? coeffs_[i] : 0;
    }

    [[nodiscard]] bool is_zero() const noexcept {
        return coeffs_.size() == 1 && coeffs_[0] == 0;
    }

    [[nodiscard]] bool is_one() const noexcept {
        return coeffs_.size() == 1 && coeffs_[0] == 1;
    }

    Polynomial& operator+=(const Polynomial &rhs) {
        size_t max_sz = std::max(coeffs_.size(), rhs.coeffs_.size());
        coeffs_.resize(max_sz, 0);
        for (size_t i = 0; i < rhs.coeffs_.size(); ++i) {
            coeffs_[i] = (coeffs_[i] + rhs.coeffs_[i]) % mod_;
        }
        normalize();
        return *this;
    }

    Polynomial& operator-=(const Polynomial &rhs) {
        size_t max_sz = std::max(coeffs_.size(), rhs.coeffs_.size());
        coeffs_.resize(max_sz, 0);
        for (size_t i = 0; i < rhs.coeffs_.size(); ++i) {
            coeffs_[i] = (coeffs_[i] - rhs.coeffs_[i] + mod_) % mod_;
        }
        normalize();
        return *this;
    }

    friend Polynomial operator+(Polynomial lhs, const Polynomial &rhs) {
        lhs += rhs;
        return lhs;
    }

    friend Polynomial operator-(Polynomial lhs, const Polynomial &rhs) {
        lhs -= rhs;
        return lhs;
    }

    friend Polynomial operator*(const Polynomial &a, const Polynomial &b) {
        if (a.is_zero() || b.is_zero()) return Polynomial(a.mod_);
        std::vector<int> res(a.coeffs_.size() + b.coeffs_.size() - 1, 0);
        for (size_t i = 0; i < a.coeffs_.size(); ++i) {
            for (size_t j = 0; j < b.coeffs_.size(); ++j) {
                res[i + j] = (res[i + j] + a.coeffs_[i] * b.coeffs_[j]) % a.mod_;
            }
        }
        return Polynomial(std::move(res), a.mod_);
    }

    /* Ділення з остачею: повертає пару {частка, остача} */
    static std::pair<Polynomial, Polynomial> div_rem(const Polynomial &a, const Polynomial &b) {
        if (b.is_zero()) {
            throw std::invalid_argument("Ділення на нульовий многочлен");
        }
        if (a.degree() < b.degree()) {
            return {Polynomial(a.mod_), a};
        }

        Polynomial rem = a;
        std::vector<int> q_coeffs(a.degree() - b.degree() + 1, 0);
        int b_lead_inv = mod_inverse(b.coeffs_.back(), a.mod_);

        while (rem.degree() >= b.degree() && !rem.is_zero()) {
            int shift = rem.degree() - b.degree();
            int factor = (rem.coeffs_.back() * b_lead_inv) % a.mod_;
            q_coeffs[shift] = factor;

            for (size_t i = 0; i < b.coeffs_.size(); ++i) {
                int sub_val = (factor * b.coeffs_[i]) % a.mod_;
                rem.coeffs_[i + shift] = (rem.coeffs_[i + shift] - sub_val + a.mod_) % a.mod_;
            }
            rem.normalize();
        }

        return {Polynomial(std::move(q_coeffs), a.mod_), rem};
    }

    friend Polynomial operator/(const Polynomial &a, const Polynomial &b) {
        return div_rem(a, b).first;
    }

    friend Polynomial operator%(const Polynomial &a, const Polynomial &b) {
        return div_rem(a, b).second;
    }

    /* Найбільший спільний дільник (НСД) */
    static Polynomial gcd(Polynomial a, Polynomial b) {
        while (!b.is_zero()) {
            a = a % b;
            std::swap(a, b);
        }
        if (!a.is_zero() && a.coeffs_.back() != 1) {
            int inv = mod_inverse(a.coeffs_.back(), a.mod_);
            for (auto &c : a.coeffs_) {
                c = (c * inv) % a.mod_;
            }
        }
        return a;
    }

    /* Піднесення до степеня за модулем многочлена */
    static Polynomial pow_mod(Polynomial base, int exp, const Polynomial &mod_poly) {
        Polynomial res({1}, base.mod_);
        base = base % mod_poly;
        while (exp > 0) {
            if (exp & 1) {
                res = (res * base) % mod_poly;
            }
            base = (base * base) % mod_poly;
            exp >>= 1;
        }
        return res;
    }

    /* Перевірка незвідності за алгоритмом Рабіна */
    [[nodiscard]] bool is_irreducible() const {
        if (degree() <= 1) return degree() == 1;

        Polynomial x_poly({0, 1}, mod_); /* x */
        Polynomial h = x_poly;

        /* Перевірка умови: x^(p^n) mod f(x) == x */
        for (int i = 0; i < degree(); ++i) {
            h = pow_mod(h, mod_, *this);
        }
        if (!(h - x_poly).is_zero()) {
            return false;
        }

        /* Перевірка відсутності спільних дільників зі степенями d | n */
        int n = degree();
        for (int d = 1; d <= n / 2; ++d) {
            if (n % d == 0) {
                Polynomial hd = x_poly;
                for (int i = 0; i < d; ++i) {
                    hd = pow_mod(hd, mod_, *this);
                }
                Polynomial g = gcd(hd - x_poly, *this);
                if (g.degree() > 0) {
                    return false;
                }
            }
        }
        return true;
    }

    void print() const {
        bool first = true;
        for (int i = degree(); i >= 0; --i) {
            if (coeffs_[i] == 0 && degree() > 0) continue;
            if (!first) std::cout << " + ";
            if (i == 0) std::cout << coeffs_[i];
            else if (i == 1) {
                if (coeffs_[i] == 1) std::cout << "x";
                else std::cout << coeffs_[i] << "*x";
            } else {
                if (coeffs_[i] == 1) std::cout << "x^" << i;
                else std::cout << coeffs_[i] << "*x^" << i;
            }
            first = false;
        }
        std::cout << "\n";
    }
};

int main() {
    std::cout << "=== Факторизація та перевірка незвідності на C++20 ===\n\n";

    /* Стандартний непривідний многочлен AES Rijndael: x^8 + x^4 + x^3 + x + 1 над F_2 */
    Polynomial aes_poly({1, 1, 0, 1, 1, 0, 0, 0, 1}, 2);
    std::cout << "Многочлен AES: ";
    aes_poly.print();
    std::cout << "Статус: " << (aes_poly.is_irreducible() ? "НЕПРИВІДНИЙ" : "ЗВІДНИЙ") << "\n\n";

    /* Складений многочлен: (x^3 + x + 1) * (x^4 + x + 1) над F_2 */
    Polynomial factor_a({1, 1, 0, 1}, 2);       // x^3 + x + 1
    Polynomial factor_b({1, 1, 0, 0, 1}, 2);    // x^4 + x + 1
    Polynomial composite = factor_a * factor_b;

    std::cout << "Складений многочлен: ";
    composite.print();
    std::cout << "Статус: " << (composite.is_irreducible() ? "НЕПРИВІДНИЙ" : "ЗВІДНИЙ") << "\n\n";

    /* Розділення множників за методом Distinct-Degree */
    std::cout << "Факторизація Distinct-Degree:\n";
    Polynomial current = composite;
    Polynomial x_poly({0, 1}, 2);
    Polynomial h = x_poly;

    for (int d = 1; d <= current.degree() / 2; ++d) {
        h = Polynomial::pow_mod(h, 2, current);
        Polynomial diff = h - x_poly;
        Polynomial factor = Polynomial::gcd(diff, current);
        if (factor.degree() > 0) {
            std::cout << "  Виділено незвідний множник степеня " << d << ": ";
            factor.print();
            current = current / factor;
        }
    }
    if (current.degree() > 0) {
        std::cout << "  Залишковий незвідний множник степеня " << current.degree() << ": ";
        current.print();
    }

    return 0;
}
