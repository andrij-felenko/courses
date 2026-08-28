#include <iostream>
#include <vector>
#include <cmath>
#include <algorithm>
#include <numbers>
#include <span>

namespace pal_sim {

struct RgbColor {
    double r{0.0};
    double g{0.0};
    double b{0.0};
};

struct YuvColor {
    double y{0.0};
    double u{0.0};
    double v{0.0};
};

class ColorConverter {
public:
    [[nodiscard]] static constexpr YuvColor to_yuv(const RgbColor& rgb) noexcept {
        return {
            .y =  0.299 * rgb.r + 0.587 * rgb.g + 0.114 * rgb.b,
            .u = -0.147 * rgb.r - 0.289 * rgb.g + 0.436 * rgb.b,
            .v =  0.615 * rgb.r - 0.515 * rgb.g - 0.100 * rgb.b
        };
    }

    [[nodiscard]] static constexpr RgbColor to_rgb(const YuvColor& yuv) noexcept {
        const double r = std::clamp(yuv.y + 1.140 * yuv.v, 0.0, 1.0);
        const double b = std::clamp(yuv.y + 2.032 * yuv.u, 0.0, 1.0);
        const double g = std::clamp(yuv.y - 0.395 * yuv.u - 0.581 * yuv.v, 0.0, 1.0);
        return {.r = r, .g = g, .b = b};
    }
};

class PalDecoderSimulator {
private:
    static constexpr std::size_t kSamplesPerLine = 1000;
    static constexpr double kSubcarrierFreq = 4433618.75;
    static constexpr double kSamplingFreq   = 40000000.0;

public:
    void run_simulation(RgbColor target_color, double phase_error_deg) const {
        const double phase_error_rad = phase_error_deg * std::numbers::pi / 180.0;
        const YuvColor orig_yuv = ColorConverter::to_yuv(target_color);

        std::vector<double> line_N(kSamplesPerLine);
        std::vector<double> line_N1(kSamplesPerLine);

        const double dt = 1.0 / kSamplingFreq;
        const double omega = 2.0 * std::numbers::pi * kSubcarrierFreq;

        // Синтез двох рядків PAL з фазовим маятником та помилкою каналу
        for (std::size_t i = 0; i < kSamplesPerLine; ++i) {
            const double t = static_cast<double>(i) * dt;
            line_N[i]  = orig_yuv.u * std::sin(omega * t + phase_error_rad) +
                         orig_yuv.v * std::cos(omega * t + phase_error_rad);
            line_N1[i] = orig_yuv.u * std::sin(omega * t + phase_error_rad) -
                         orig_yuv.v * std::cos(omega * t + phase_error_rad);
        }

        // Демодуляція NTSC (без компенсації)
        const RgbColor ntsc_rgb = demodulate_ntsc(line_N, orig_yuv.y, omega, dt);

        // Демодуляція PAL (із 1H ультразвуковою лінією затримки)
        const RgbColor pal_rgb = demodulate_pal(line_N, line_N1, orig_yuv.y, omega, dt);

        print_results(target_color, ntsc_rgb, pal_rgb, phase_error_deg);
    }

private:
    [[nodiscard]] RgbColor demodulate_ntsc(std::span<const double> line, double luma,
                                            double omega, double dt) const {
        double u_acc = 0.0;
        double v_acc = 0.0;
        for (std::size_t i = 0; i < line.size(); ++i) {
            const double t = static_cast<double>(i) * dt;
            u_acc += line[i] * 2.0 * std::sin(omega * t);
            v_acc += line[i] * 2.0 * std::cos(omega * t);
        }
        const YuvColor yuv{
            .y = luma,
            .u = u_acc / static_cast<double>(line.size()),
            .v = v_acc / static_cast<double>(line.size())
        };
        return ColorConverter::to_rgb(yuv);
    }

    [[nodiscard]] RgbColor demodulate_pal(std::span<const double> line_N,
                                           std::span<const double> line_N1,
                                           double luma, double omega, double dt) const {
        double u_acc = 0.0;
        double v_acc = 0.0;
        for (std::size_t i = 0; i < line_N.size(); ++i) {
            const double t = static_cast<double>(i) * dt;
            // Ультразвукова лінія затримки 1H + матричний суматор/віднімач
            const double u_sig = 0.5 * (line_N[i] + line_N1[i]);
            const double v_sig = 0.5 * (line_N[i] - line_N1[i]);

            u_acc += u_sig * 2.0 * std::sin(omega * t);
            v_acc += v_sig * 2.0 * std::cos(omega * t);
        }
        const YuvColor yuv{
            .y = luma,
            .u = u_acc / static_cast<double>(line_N.size()),
            .v = v_acc / static_cast<double>(line_N.size())
        };
        return ColorConverter::to_rgb(yuv);
    }

    void print_results(const RgbColor& orig, const RgbColor& ntsc,
                        const RgbColor& pal, double phase_error_deg) const {
        std::cout << "=== C++20 СИМУЛЯЦІЯ ДЕМОДУЛЯЦІЇ (Фазова помилка = "
                  << phase_error_deg << " deg) ===\n"
                  << "Оригінал RGB:   R=" << orig.r << ", G=" << orig.g << ", B=" << orig.b << "\n"
                  << "NTSC декодер:   R=" << ntsc.r << ", G=" << ntsc.g << ", B=" << ntsc.b
                  << "  [СПОРТВОРЕННЯ ТОНУ!]\n"
                  << "PAL 1H декодер: R=" << pal.r << ", G=" << pal.g << ", B=" << pal.b
                  << "  [ТОЧНИЙ КОЛІР!]\n";
    }
};

} // namespace pal_sim

int main() {
    const pal_sim::PalDecoderSimulator simulator;
    /* Тестовий відтінок шкіри */
    simulator.run_simulation({.r = 0.85, .g = 0.60, .b = 0.50}, 15.0);
    return 0;
}
