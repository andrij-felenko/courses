#include <iostream>
#include <complex>
#include <array>
#include <vector>
#include <cmath>
#include <iomanip>

namespace Polarization {

using Complex = std::complex<double>;

/* Вектор Джонса 2x1 */
struct JonesVector {
    Complex ex{1.0, 0.0};
    Complex ey{0.0, 0.0};

    [[nodiscard]] double intensity() const noexcept {
        return std::norm(ex) + std::norm(ey);
    }
};

/* Матриця Джонса 2x2 */
class JonesMatrix {
private:
    std::array<std::array<Complex, 2>, 2> m_{};

public:
    JonesMatrix() {
        m_[0][0] = 1.0; m_[0][1] = 0.0;
        m_[1][0] = 0.0; m_[1][1] = 1.0;
    }

    JonesMatrix(Complex m00, Complex m01, Complex m10, Complex m11) {
        m_[0][0] = m00; m_[0][1] = m01;
        m_[1][0] = m10; m_[1][1] = m11;
    }

    [[nodiscard]] Complex operator()(size_t r, size_t c) const {
        return m_.at(r).at(c);
    }

    [[nodiscard]] JonesVector operator*(const JonesVector& j) const noexcept {
        return JonesVector{
            m_[0][0] * j.ex + m_[0][1] * j.ey,
            m_[1][0] * j.ex + m_[1][1] * j.ey
        };
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

    /* Генератор поляризатора під кутом theta (рад) */
    static JonesMatrix Polarizer(double theta_rad) {
        double c = std::cos(theta_rad);
        double s = std::sin(theta_rad);
        return JonesMatrix(c * c, c * s, c * s, s * s);
    }

    /* Генератор фазової платівки (retarder) */
    static JonesMatrix Retarder(double theta_rad, double delta_rad) {
        double c = std::cos(theta_rad);
        double s = std::sin(theta_rad);
        Complex phase = std::polar(1.0, delta_rad);

        JonesMatrix J0(1.0, 0.0, 0.0, phase);
        JonesMatrix R(c, s, -s, c);
        JonesMatrix R_inv(c, -s, s, c);

        return R_inv * J0 * R;
    }
};

/* Клас вектора Стокса 4x1 */
struct StokesVector {
    double s0{1.0};
    double s1{0.0};
    double s2{0.0};
    double s3{0.0};

    [[nodiscard]] double degreeOfPolarization() const noexcept {
        if (s0 <= 1e-15) return 0.0;
        double pol = std::sqrt(s1 * s1 + s2 * s2 + s3 * s3);
        return pol / s0;
    }

    static StokesVector fromJones(const JonesVector& j) noexcept {
        double ix = std::norm(j.ex);
        double iy = std::norm(j.ey);
        Complex ex_ey_c = j.ex * std::conj(j.ey);

        return StokesVector{
            ix + iy,
            ix - iy,
            2.0 * ex_ey_c.real(),
            -2.0 * ex_ey_c.imag()
        };
    }
};

/* Клас каскаду оптичного тракту */
class OpticalCascade {
private:
    std::vector<JonesMatrix> elements_;

public:
    void addElement(const JonesMatrix& m) {
        elements_.push_back(m);
    }

    [[nodiscard]] JonesVector process(const JonesVector& input) const {
        JonesVector current = input;
        for (const auto& elem : elements_) {
            current = elem * current;
        }
        return current;
    }
};

} // namespace Polarization

int main() {
    using namespace Polarization;
    constexpr double PI = 3.14159265358979323846;

    std::cout << std::fixed << std::setprecision(4);
    std::cout << "=== Симулятор поляризаційного тракту (C++) ===\n";

    JonesVector j_in{Complex{1.0, 0.0}, Complex{0.0, 0.0}};

    OpticalCascade cascade;
    // 1. Чвертьхвильова платівка QWP під 45°
    cascade.addElement(JonesMatrix::Retarder(45.0 * PI / 180.0, PI / 2.0));
    // 2. Лінійний поляризатор 90°
    cascade.addElement(JonesMatrix::Polarizer(90.0 * PI / 180.0));

    JonesVector j_out = cascade.process(j_in);
    StokesVector s_out = StokesVector::fromJones(j_out);

    std::cout << "Вихідний вектор Джонса: Ex=" << j_out.ex << ", Ey=" << j_out.ey << "\n";
    std::cout << "Вектор Стокса: S0=" << s_out.s0 << ", S1=" << s_out.s1
              << ", S2=" << s_out.s2 << ", S3=" << s_out.s3 << "\n";
    std::cout << "Ступінь поляризації (DOP): " << s_out.degreeOfPolarization() << "\n";

    return 0;
}
