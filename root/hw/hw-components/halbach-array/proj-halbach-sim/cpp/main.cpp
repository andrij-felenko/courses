#include <iostream>
#include <vector>
#include <cmath>
#include <numbers>
#include <format>
#include <span>

struct Vec2D {
    double x{0.0};
    double y{0.0};

    [[nodiscard]] constexpr double magnitude_sq() const noexcept {
        return x * x + y * y;
    }

    [[nodiscard]] double magnitude() const noexcept {
        return std::hypot(x, y);
    }

    constexpr Vec2D& operator+=(const Vec2D& other) noexcept {
        x += other.x;
        y += other.y;
        return *this;
    }
};

struct MagnetBlock {
    double x_min{0.0};
    double x_max{0.0};
    double y_min{0.0};
    double y_max{0.0};
    double mx{0.0}; // Намагніченість X, А/м
    double my{0.0}; // Намагніченість Y, А/м
};

class HalbachSimulator {
public:
    static constexpr double Mu0 = 4.0 * std::numbers::pi * 1e-7;
    static constexpr double Epsilon = 1e-9;

    [[nodiscard]] static Vec2D compute_block_field(const MagnetBlock& b, double x, double y) noexcept {
        const double vx[4] = {b.x_min, b.x_max, b.x_max, b.x_min};
        const double vy[4] = {b.y_min, b.y_min, b.y_max, b.y_max};
        const double signs[4] = {+1.0, -1.0, +1.0, -1.0};

        double bx_sum = 0.0;
        double by_sum = 0.0;

        for (std::size_t k = 0; k < 4; ++k) {
            const double dx = x - vx[k];
            const double dy = y - vy[k];
            double r_sq = dx * dx + dy * dy;

            if (r_sq < Epsilon * Epsilon) {
                r_sq = Epsilon * Epsilon;
            }

            const double r = std::sqrt(r_sq);
            const double log_r = std::log(r);
            const double theta = std::atan2(dy, dx);
            const double s = signs[k];

            bx_sum += s * (b.my * log_r + b.mx * theta);
            by_sum += s * (b.my * theta - b.mx * log_r);
        }

        const double factor = Mu0 / (2.0 * std::numbers::pi);
        return Vec2D{factor * bx_sum, factor * by_sum};
    }

    [[nodiscard]] static Vec2D compute_array_field(std::span<const MagnetBlock> blocks, double x, double y) noexcept {
        Vec2D total{};
        for (const auto& block : blocks) {
            total += compute_block_field(block, x, y);
        }
        return total;
    }
};

int main() {
    constexpr std::size_t num_segments = 5;
    constexpr double block_width = 0.010;  // 10 мм
    constexpr double block_height = 0.010; // 10 мм
    constexpr double remanence_br = 1.40;  // NdFeB N48
    constexpr double m_val = remanence_br / HalbachSimulator::Mu0;

    std::vector<MagnetBlock> halbach(num_segments);
    std::vector<MagnetBlock> conventional(num_segments);

    constexpr double h_dirs[5][2] = {
        { 0.0, +1.0}, // ↑ N
        {+1.0,  0.0}, // → E
        { 0.0, -1.0}, // ↓ S
        {-1.0,  0.0}, // ← W
        { 0.0, +1.0}  // ↑ N
    };

    constexpr double c_dirs[5][2] = {
        {0.0, +1.0},
        {0.0, -1.0},
        {0.0, +1.0},
        {0.0, -1.0},
        {0.0, +1.0}
    };

    for (std::size_t i = 0; i < num_segments; ++i) {
        const double x0 = static_cast<double>(i) * block_width;
        const double x1 = x0 + block_width;
        const double y0 = -block_height;
        const double y1 = 0.0;

        halbach[i] = MagnetBlock{x0, x1, y0, y1, h_dirs[i][0] * m_val, h_dirs[i][1] * m_val};
        conventional[i] = MagnetBlock{x0, x1, y0, y1, c_dirs[i][0] * m_val, c_dirs[i][1] * m_val};
    }

    std::cout << "=== ПЕРЕВІРКА СУПЕРПОЗИЦІЇ МАСИВУ ГАЛЬБАХА (C++) ===\n\n";

    constexpr double test_x = 0.025; // x = 25 мм
    constexpr double airgap = 0.002; // z = 2 мм
    constexpr double y_weak = -block_height - airgap;

    const auto b_h_strong = HalbachSimulator::compute_array_field(halbach, test_x, +airgap);
    const auto b_h_weak   = HalbachSimulator::compute_array_field(halbach, test_x, y_weak);
    const auto b_c_strong = HalbachSimulator::compute_array_field(conventional, test_x, +airgap);
    const auto b_c_weak   = HalbachSimulator::compute_array_field(conventional, test_x, y_weak);

    const double mod_h_strong = b_h_strong.magnitude();
    const double mod_h_weak   = b_h_weak.magnitude();
    const double mod_c_strong = b_c_strong.magnitude();

    std::cout << std::format("  Масив Гальбаха:  |B_сильний| = {:.4f} Тл, |B_слабкий| = {:.4f} Тл\n", 
                             mod_h_strong, mod_h_weak);
    std::cout << std::format("  Звичайний масив: |B_сильний| = {:.4f} Тл, |B_слабкий| = {:.4f} Тл\n", 
                             mod_c_strong, b_c_weak.magnitude());
    std::cout << std::format("  Коефіцієнт підсилення на робочому боці: {:.2f} x\n", 
                             mod_h_strong / mod_c_strong);
    std::cout << std::format("  Коефіцієнт пригнічення слабкого боку:   {:.2f} x (у {} разів менше)\n",
                             mod_h_weak / mod_h_strong, static_cast<int>(mod_h_strong / mod_h_weak));

    return 0;
}
