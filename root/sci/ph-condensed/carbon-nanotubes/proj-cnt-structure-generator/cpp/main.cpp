#include <iostream>
#include <vector>
#include <cmath>
#include <numbers>
#include <algorithm>
#include <stdexcept>
#include <iomanip>

struct Atom3D {
    double x{0.0};
    double y{0.0};
    double z{0.0};
};

struct CNTProperties {
    int n{0};
    int m{0};
    double diameter_nm{0.0};
    double chiral_angle_deg{0.0};
    bool is_metal{false};
    double band_gap_eV{0.0};
};

class CarbonNanotube {
public:
    static constexpr double a_cc = 0.142;          // Довжина зв'язку C-C (нм)
    static constexpr double tight_binding_t = 2.7; // Інтеграл перескоку (еВ)

    CarbonNanotube(int n, int m) : n_(n), m_(m) {
        if (n < 0 || m < 0 || (n == 0 && m == 0)) {
            throw std::invalid_argument("Індекси хіральності повинні бути додатними.");
        }
    }

    [[nodiscard]] CNTProperties properties() const {
        CNTProperties props;
        props.n = n_;
        props.m = m_;

        const double a = a_cc * std::sqrt(3.0);
        const double l_circ = a * std::sqrt(n_ * n_ + n_ * m_ + m_ * m_);
        props.diameter_nm = l_circ / std::numbers::pi;

        const double cos_theta = (2.0 * n_ + m_) / (2.0 * std::sqrt(n_ * n_ + n_ * m_ + m_ * m_));
        props.chiral_angle_deg = std::acos(std::clamp(cos_theta, -1.0, 1.0)) * (180.0 / std::numbers::pi);

        props.is_metal = ((n_ - m_) % 3 == 0);
        props.band_gap_eV = props.is_metal ? 0.0 : (2.0 * a_cc * tight_binding_t) / props.diameter_nm;

        return props;
    }

    [[nodiscard]] std::vector<Atom3D> generate_ring(size_t num_atoms) const {
        const double diameter = properties().diameter_nm;
        const double radius = diameter / 2.0;
        std::vector<Atom3D> ring;
        ring.reserve(num_atoms);

        for (size_t i = 0; i < num_atoms; ++i) {
            const double phi = (2.0 * std::numbers::pi * static_cast<double>(i)) / static_cast<double>(num_atoms);
            ring.push_back({
                .x = radius * std::cos(phi),
                .y = radius * std::sin(phi),
                .z = 0.0
            });
        }
        return ring;
    }

private:
    int n_;
    int m_;
};

int main() {
    try {
        CarbonNanotube cnt(10, 10); // Кріслова (10, 10)
        const auto props = cnt.properties();

        std::cout << std::fixed << std::setprecision(4);
        std::cout << "Параметри CNT (" << props.n << ", " << props.m << "):\n";
        std::cout << "  Діаметр: " << props.diameter_nm << " нм\n";
        std::cout << "  Кут хіральності: " << props.chiral_angle_deg << "°\n";
        std::cout << "  Тип провідності: " << (props.is_metal ? "Металевий" : "Напівпровідниковий") << "\n";
        std::cout << "  Заборонена зона E_g: " << props.band_gap_eV << " eV\n";
    } catch (const std::exception& e) {
        std::cerr << "Помилка: " << e.what() << '\n';
        return 1;
    }
    return 0;
}
