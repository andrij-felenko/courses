#include <iostream>
#include <vector>
#include <complex>
#include <cmath>
#include <span>
#include <stdexcept>
#include <string_view>
#include <iomanip>

class DirichletSeries {
private:
    std::vector<double> coeff_;

public:
    explicit DirichletSeries(size_t size, double initial_val = 0.0)
        : coeff_(size + 1, initial_val) {
        if (!coeff_.empty()) {
            coeff_[0] = 0.0; /* Нульовий індекс не використовується в 1-індексації */
        }
    }

    /* Фабричні методи створення типових рядів */
    static DirichletSeries constant(size_t size, double c = 1.0) {
        DirichletSeries ds(size);
        for (size_t i = 1; i <= size; ++i) {
            ds[i] = c;
        }
        return ds;
    }

    static DirichletSeries identity(size_t size) {
        DirichletSeries ds(size);
        for (size_t i = 1; i <= size; ++i) {
            ds[i] = static_cast<double>(i);
        }
        return ds;
    }

    size_t size() const noexcept { return coeff_.size() - 1; }

    double& operator[](size_t idx) { return coeff_[idx]; }
    double operator[](size_t idx) const { return coeff_[idx]; }

    std::span<const double> span() const noexcept {
        return std::span<const double>(coeff_.data() + 1, size());
    }

    /* Оцінка значення ряду у комплексній точці s */
    std::complex<double> evaluate(std::complex<double> s) const {
        std::complex<double> sum(0.0, 0.0);
        for (size_t n = 1; n <= size(); ++n) {
            if (coeff_[n] == 0.0) continue;
            double n_val = static_cast<double>(n);
            /* n⁻ˢ = exp(-s * ln(n)) */
            std::complex<double> term = std::exp(-s * std::log(n_val));
            sum += coeff_[n] * term;
        }
        return sum;
    }

    /* Ситоподібна згортка за O(N log N) */
    DirichletSeries convolve(const DirichletSeries& other) const {
        size_t min_n = std::min(size(), other.size());
        DirichletSeries result(min_n);

        for (size_t i = 1; i <= min_n; ++i) {
            if (coeff_[i] == 0.0) continue;
            for (size_t j = 1; i * j <= min_n; ++j) {
                result[i * j] += coeff_[i] * other[j];
            }
        }
        return result;
    }

    /* Обчислення оберненого ряду за рекурентною схемою */
    DirichletSeries invert() const {
        if (size() == 0 || coeff_[1] == 0.0) {
            throw std::invalid_argument("Ряд Діріхле з a[1] = 0 є необоротним.");
        }

        DirichletSeries inv(size());
        inv[1] = 1.0 / coeff_[1];

        for (size_t n = 2; n <= size(); ++n) {
            double sum = 0.0;
            for (size_t d = 2; d <= n; ++d) {
                if (n % d == 0) {
                    sum += coeff_[d] * inv[n / d];
                }
            }
            inv[n] = -sum / coeff_[1];
        }
        return inv;
    }

    /* Друк коефіцієнтів ряду */
    void print(std::string_view name) const {
        std::cout << "Ряд " << name << " (розмір N = " << size() << "):\n";
        for (size_t i = 1; i <= size(); ++i) {
            std::cout << "  " << name << "(" << i << ") = "
                      << std::setw(6) << std::fixed << std::setprecision(2)
                      << coeff_[i] << "\n";
        }
    }
};

/* Оператори перевантаження для зручності */
inline DirichletSeries operator*(const DirichletSeries& a, const DirichletSeries& b) {
    return a.convolve(b);
}

int main() {
    constexpr size_t N = 10;

    /* 1. Створення Дзета-ряду ζ(s): 1(n) = 1 */
    DirichletSeries zeta = DirichletSeries::constant(N, 1.0);

    /* 2. Згортка ζ * ζ = d(n) (число дільників) */
    DirichletSeries d_func = zeta * zeta;
    d_func.print("d (число дільників ζ²)");

    /* 3. Обернення ζ⁻¹ = μ(n) (функція Мебіуса) */
    DirichletSeries mobius = zeta.invert();
    mobius.print("μ (функція Мебіуса ζ⁻¹)");

    /* 4. Степенева функція N(n) = n */
    DirichletSeries id_func = DirichletSeries::identity(N);

    /* 5. Обчислення функції Ейлера φ = μ * N */
    DirichletSeries phi = mobius * id_func;
    phi.print("φ (функція Ейлера μ * N)");

    /* 6. Оцінка значення ζ(2.0 + 3.5i) */
    std::complex<double> s(2.0, 3.5);
    std::complex<double> val = zeta.evaluate(s);
    std::cout << "\nЧисельне значення ζ(2.0 + 3.5i) (N = " << N << "): "
              << std::setprecision(5) << val.real() << " + " << val.imag() << "i\n";

    return 0;
}
