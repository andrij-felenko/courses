#include <iostream>
#include <vector>
#include <cmath>
#include <numbers>
#include <string>
#include <span>
#include <memory>

// Конфігурація генератора сигналів
struct LissajousConfig {
    double amp_x{1.0};       // Амплітуда X
    double amp_y{1.0};       // Амплітуда Y
    double freq_x{100.0};    // Частота X (Гц)
    double freq_y{100.0};    // Частота Y (Гц)
    double phase_rad{0.0};   // Зсув фази (радіани)
};

// Двовимірна точка
struct Point2D {
    double x{0.0};
    double y{0.0};
};

// RAII-клас віртуального растрового екрана осцилографа
class VirtualOscilloscope {
public:
    VirtualOscilloscope(size_t width, size_t height)
        : width_(width), height_(height), buffer_(width * height, ' ') {}

    void clear() {
        std::fill(buffer_.begin(), buffer_.end(), ' ');
    }

    void draw_point(int px, int py, char symbol = '*') {
        if (px >= 0 && px < static_cast<int>(width_) &&
            py >= 0 && py < static_cast<int>(height_)) {
            buffer_[static_cast<size_t>(py) * width_ + static_cast<size_t>(px)] = symbol;
        }
    }

    void draw_axes() {
        int cx = static_cast<int>(width_ / 2);
        int cy = static_cast<int>(height_ / 2);
        for (size_t x = 0; x < width_; ++x) draw_point(static_cast<int>(x), cy, '-');
        for (size_t y = 0; y < height_; ++y) draw_point(cx, static_cast<int>(y), '|');
        draw_point(cx, cy, '+');
    }

    void render_trajectory(std::span<const Point2D> points) {
        int cx = static_cast<int>(width_ / 2);
        int cy = static_cast<int>(height_ / 2);

        for (const auto& pt : points) {
            int px = cx + static_cast<int>(std::round(pt.x));
            int py = cy - static_cast<int>(std::round(pt.y));
            draw_point(px, py, '#');
        }
    }

    void print() const {
        for (size_t y = 0; y < height_; ++y) {
            for (size_t x = 0; x < width_; ++x) {
                std::cout << buffer_[y * width_ + x];
            }
            std::cout << '\n';
        }
    }

    [[nodiscard]] size_t width() const noexcept { return width_; }
    [[nodiscard]] size_t height() const noexcept { return height_; }

private:
    size_t width_;
    size_t height_;
    std::vector<char> buffer_;
};

// Генератор точок траєкторії Ліссажу
class LissajousGenerator {
public:
    static std::vector<Point2D> generate(const LissajousConfig& cfg, size_t num_samples) {
        std::vector<Point2D> points;
        points.reserve(num_samples);

        double max_f = std::max(cfg.freq_x, cfg.freq_y);
        double dt = 1.0 / (max_f * 100.0); // 100 точок на один період

        for (size_t i = 0; i < num_samples; ++i) {
            double t = static_cast<double>(i) * dt;
            double x = cfg.amp_x * std::sin(2.0 * std::numbers::pi * cfg.freq_x * t + cfg.phase_rad);
            double y = cfg.amp_y * std::sin(2.0 * std::numbers::pi * cfg.freq_y * t);
            points.push_back({x, y});
        }

        return points;
    }
};

int main() {
    constexpr size_t width = 61;
    constexpr size_t height = 25;
    constexpr size_t num_samples = 600;

    VirtualOscilloscope scope(width, height);
    scope.draw_axes();

    LissajousConfig config{
        .amp_x = static_cast<double>(width / 2 - 2),
        .amp_y = static_cast<double>(height / 2 - 2),
        .freq_x = 100.0,
        .freq_y = 200.0,
        .phase_rad = std::numbers::pi / 4.0 // 45 градуси
    };

    std::vector<Point2D> trajectory = LissajousGenerator::generate(config, num_samples);
    scope.render_trajectory(trajectory);

    std::cout << "=== Modern C++ Lissajous Scope (1:2 ratio, pi/4 phase) ===\n\n";
    scope.print();

    return 0;
}
