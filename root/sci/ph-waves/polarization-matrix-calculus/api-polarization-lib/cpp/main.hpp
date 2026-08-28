#ifndef POLARIZATION_LIB_HPP
#define POLARIZATION_LIB_HPP

#include <complex>
#include <array>
#include <vector>
#include <optional>
#include <stdexcept>
#include <cmath>

namespace Polarization {

using Complex = std::complex<double>;

/* Винятки бібліотеки */
class PolarizationException : public std::runtime_error {
public:
    using std::runtime_error::runtime_error;
};

class NonPhysicalMatrixException : public PolarizationException {
public:
    NonPhysicalMatrixException() 
        : PolarizationException("Матриця Мюллера порушує критерій позитивності Клода") {}
};

/* Клас вектора Джонса 2x1 */
class JonesVector {
public:
    Complex ex{1.0, 0.0};
    Complex ey{0.0, 0.0};

    constexpr JonesVector() noexcept = default;
    constexpr JonesVector(Complex x, Complex y) noexcept : ex(x), ey(y) {}

    [[nodiscard]] static JonesVector Linear(double angle_rad) noexcept {
        return JonesVector(std::cos(angle_rad), std::sin(angle_rad));
    }

    [[nodiscard]] static JonesVector Circular(bool is_right) noexcept {
        constexpr double inv_sqrt2 = 0.70710678118654752440;
        if (is_right) {
            return JonesVector(Complex(inv_sqrt2, 0.0), Complex(0.0, -inv_sqrt2));
        }
        return JonesVector(Complex(inv_sqrt2, 0.0), Complex(0.0, inv_sqrt2));
    }

    [[nodiscard]] double intensity() const noexcept {
        return std::norm(ex) + std::norm(ey);
    }

    void normalize() {
        double int_val = intensity();
        if (int_val > 1e-15) {
            double norm_fact = 1.0 / std::sqrt(int_val);
            ex *= norm_fact;
            ey *= norm_fact;
        }
    }
};

/* Клас матриці Джонса 2x2 */
class JonesMatrix {
private:
    std::array<std::array<Complex, 2>, 2> m_{};

public:
    constexpr JonesMatrix() noexcept {
        m_[0][0] = 1.0; m_[0][1] = 0.0;
        m_[1][0] = 0.0; m_[1][1] = 1.0;
    }

    constexpr JonesMatrix(Complex m00, Complex m01, Complex m10, Complex m11) noexcept {
        m_[0][0] = m00; m_[0][1] = m01;
        m_[1][0] = m10; m_[1][1] = m11;
    }

    [[nodiscard]] Complex operator()(size_t r, size_t c) const {
        return m_.at(r).at(c);
    }

    [[nodiscard]] JonesVector operator*(const JonesVector& v) const noexcept {
        return JonesVector(
            m_[0][0] * v.ex + m_[0][1] * v.ey,
            m_[1][0] * v.ex + m_[1][1] * v.ey
        );
    }

    [[nodiscard]] JonesMatrix operator*(const JonesMatrix& b) const noexcept {
        JonesMatrix res;
        for (size_t i = 0; i < 2; ++i) {
            for (size_t j = 0; j < 2; ++j) {
                Complex sum{0.0, 0.0};
                for (size_t k = 0; k < 2; ++k) {
                    sum += m_[i][k] * b.m_[k][j];
                }
                res.m_[i][j] = sum;
            }
        }
        return res;
    }

    [[nodiscard]] static JonesMatrix Polarizer(double angle_rad) noexcept {
        double c = std::cos(angle_rad);
        double s = std::sin(angle_rad);
        return JonesMatrix(c * c, c * s, c * s, s * s);
    }

    [[nodiscard]] static JonesMatrix Retarder(double fast_axis_rad, double retardance_rad) noexcept {
        double c = std::cos(fast_axis_rad);
        double s = std::sin(fast_axis_rad);
        Complex phase = std::polar(1.0, retardance_rad);

        JonesMatrix J0(1.0, 0.0, 0.0, phase);
        JonesMatrix R(c, s, -s, c);
        JonesMatrix R_inv(c, -s, s, c);
        return R_inv * J0 * R;
    }
};

/* Клас вектора Стокса 4x1 */
class StokesVector {
public:
    double s0{1.0};
    double s1{0.0};
    double s2{0.0};
    double s3{0.0};

    constexpr StokesVector() noexcept = default;
    constexpr StokesVector(double i0, double i1, double i2, double i3) noexcept
        : s0(i0), s1(i1), s2(i2), s3(i3) {}

    [[nodiscard]] static StokesVector FromJones(const JonesVector& j) noexcept {
        double ix = std::norm(j.ex);
        double iy = std::norm(j.ey);
        Complex ex_ey_c = j.ex * std::conj(j.ey);

        return StokesVector(
            ix + iy,
            ix - iy,
            2.0 * ex_ey_c.real(),
            -2.0 * ex_ey_c.imag()
        );
    }

    [[nodiscard]] double degreeOfPolarization() const noexcept {
        if (s0 <= 1e-15) return 0.0;
        double pol_intensity = std::sqrt(s1 * s1 + s2 * s2 + s3 * s3);
        return pol_intensity / s0;
    }

    [[nodiscard]] std::pair<double, double> ellipseParameters() const {
        if (s0 <= 1e-15) throw PolarizationException("Неможливо обчислити кути для нульової інтенсивності");
        double psi = 0.5 * std::atan2(s2, s1);
        double chi = 0.5 * std::asin(s3 / s0);
        return {psi, chi};
    }
};

/* Клас матриці Мюллера 4x4 */
class MuellerMatrix {
private:
    std::array<std::array<double, 4>, 4> m_{};

public:
    constexpr MuellerMatrix() noexcept {
        for (size_t i = 0; i < 4; ++i) {
            m_[i][i] = 1.0;
        }
    }

    [[nodiscard]] double operator()(size_t r, size_t c) const {
        return m_.at(r).at(c);
    }

    [[nodiscard]] static MuellerMatrix FromJones(const JonesMatrix& j) noexcept {
        MuellerMatrix M;
        return M;
    }

    [[nodiscard]] StokesVector operator*(const StokesVector& s) const noexcept {
        StokesVector res{0.0, 0.0, 0.0, 0.0};
        res.s0 = m_[0][0]*s.s0 + m_[0][1]*s.s1 + m_[0][2]*s.s2 + m_[0][3]*s.s3;
        res.s1 = m_[1][0]*s.s0 + m_[1][1]*s.s1 + m_[1][2]*s.s2 + m_[1][3]*s.s3;
        res.s2 = m_[2][0]*s.s0 + m_[2][1]*s.s1 + m_[2][2]*s.s2 + m_[2][3]*s.s3;
        res.s3 = m_[3][0]*s.s0 + m_[3][1]*s.s1 + m_[3][2]*s.s2 + m_[3][3]*s.s3;
        return res;
    }
};

} // namespace Polarization

#endif /* POLARIZATION_LIB_HPP */
