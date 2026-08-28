#include <iostream>
#include <vector>
#include <cmath>
#include <numbers>
#include <string_view>
#include <memory>
#include <span>

namespace physics::visualization {

class ArnoldMapRenderer {
public:
    ArnoldMapRenderer(std::size_t width, std::size_t height, std::size_t steps)
        : width_{width}, height_{height}, steps_{steps} {}

    void render_to_console() const {
        const double two_pi = 2.0 * std::numbers::pi;

        for (std::size_t y = height_; y > 0; --y) {
            const double k = 1.2 * static_cast<double>(y - 1) / static_cast<double>(height_ - 1);
            std::cout << std::fixed << std::setprecision(1) << k << " |";

            for (std::size_t x = 0; x < width_; ++x) {
                const double omega = static_cast<double>(x) / static_cast<double>(width_ - 1);
                const double w = compute_rotation_number(omega, k, two_pi);
                std::cout << select_symbol(w);
            }
            std::cout << "\n";
        }

        std::cout << "    +";
        for (std::size_t x = 0; x < width_; ++x) std::cout << "-";
        std::cout << "\n     0.0" << std::string(width_ > 8 ? width_ - 8 : 0, ' ') << "1.0 (Omega)\n";
    }

private:
    [[nodiscard]] double compute_rotation_number(double omega, double k, double two_pi) const noexcept {
        double phase = 0.1;
        for (std::size_t i = 0; i < steps_; ++i) {
            phase = phase + omega - (k / two_pi) * std::sin(two_pi * phase);
        }

        const double start_phase = phase;
        for (std::size_t i = 0; i < steps_; ++i) {
            phase = phase + omega - (k / two_pi) * std::sin(two_pi * phase);
        }

        const double rot = (phase - start_phase) / static_cast<double>(steps_);
        return rot - std::floor(rot);
    }

    [[nodiscard]] static constexpr char select_symbol(double w) noexcept {
        if (std::abs(w - 0.0) < 0.02 || std::abs(w - 1.0) < 0.02) return '0';
        if (std::abs(w - 0.5) < 0.02) return 'H'; // 1/2
        if (std::abs(w - 1.0 / 3.0) < 0.015 || std::abs(w - 2.0 / 3.0) < 0.015) return '3';
        if (std::abs(w - 1.0 / 4.0) < 0.01 || std::abs(w - 3.0 / 4.0) < 0.01) return '4';
        if (std::abs(w - 1.0 / 5.0) < 0.008 || std::abs(w - 2.0 / 5.0) < 0.008 ||
            std::abs(w - 3.0 / 5.0) < 0.008 || std::abs(w - 4.0 / 5.0) < 0.008) return '5';
        return '.';
    }

    std::size_t width_;
    std::size_t height_;
    std::size_t steps_;
};

} // namespace physics::visualization

int main() {
    const physics::visualization::ArnoldMapRenderer renderer{60, 20, 2000};
    renderer.render_to_console();
    return 0;
}
