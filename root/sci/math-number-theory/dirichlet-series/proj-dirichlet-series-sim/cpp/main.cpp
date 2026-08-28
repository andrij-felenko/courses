#include <iostream>
#include <vector>
#include <complex>
#include <cmath>
#include <span>
#include <stdexcept>

class DirichletSeries {
private:
    std::vector<double> coeff_;

public:
    explicit DirichletSeries(size_t size) : coeff_(size + 1, 0.0) {}

    size_t size() const { return coeff_.size() - 1; }

    double& operator[](size_t idx) { return coeff_[idx]; }
    double operator[](size_t idx) const { return coeff_[idx]; }

    /* Оцінка значення у комплексній точці s */
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

    /* Згортка за O(N log N) */
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

    /* Обчислення оберненого ряду */
    DirichletSeries invert() const {
        if (size() == 0 || coeff_[1] == 0.0) {
            throw std::invalid_argument("Перший коефіцієнт не може бути нулем.");
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
};

int main() {
    constexpr size_t N = 10;
    DirichletSeries zeta(N);
    for (size_t i = 1; i <= N; ++i) {
        zeta[i] = 1.0;
    }

    DirichletSeries d_func = zeta.convolve(zeta);
    std::cout << "Коефіцієнти ζ(s)² (число дільників d(n)):\n";
    for (size_t i = 1; i <= N; ++i) {
        std::cout << "d(" << i << ") = " << d_func[i] << "\n";
    }

    std::complex<double> s(2.0, 3.5);
    std::complex<double> val = zeta.evaluate(s);
    std::cout << "\nζ(2.0 + 3.5i) (зрізана до N=10): "
              << val.real() << " + " << val.imag() << "i\n";

    DirichletSeries mobius = zeta.invert();
    std::cout << "\nОбчислена функція Мебіуса μ(n) = (1/ζ)(n):\n";
    for (size_t i = 1; i <= N; ++i) {
        std::cout << "μ(" << i << ") = " << mobius[i] << "\n";
    }

    return 0;
}
