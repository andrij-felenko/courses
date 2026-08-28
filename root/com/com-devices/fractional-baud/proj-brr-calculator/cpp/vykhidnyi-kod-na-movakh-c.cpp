#include <iostream>
#include <iomanip>
#include <cmath>
#include <cstdint>
#include <string_view>
#include <optional>
#include <array>

namespace uart {

/* Структура результату розрахунку для STM32 */
struct Stm32BrrConfig {
    uint32_t bus_frequency_hz{0};
    uint32_t target_baud{0};
    uint32_t real_baud{0};
    double error_percent{0.0};
    uint16_t brr_value{0};
    uint16_t mantissa{0};
    uint8_t fraction{0};
    bool over8{false};
};

/* Структура результату розрахунку для NXP LPC */
struct NxpLpcBrrConfig {
    uint32_t bus_frequency_hz{0};
    uint32_t target_baud{0};
    uint32_t real_baud{0};
    double error_percent{0.0};
    uint16_t dll_dlm{0};
    uint8_t divaddval{0};
    uint8_t mulval{1};
};

/* Клас математичних обчислень конфігурацій дільників */
class BaudRateCalculator {
public:
    [[nodiscard]] static constexpr std::optional<Stm32BrrConfig> calculate_stm32(
        uint32_t f_ck, uint32_t target_baud, bool over8 = false) noexcept
    {
        if (f_ck == 0 || target_baud == 0) return std::nullopt;

        const double oversampling = over8 ? 8.0 : 16.0;
        const double usartdiv = static_cast<double>(f_ck) / (oversampling * static_cast<double>(target_baud));

        if (usartdiv < 1.0 || usartdiv >= 4096.0) {
            return std::nullopt;
        }

        Stm32BrrConfig cfg{};
        cfg.bus_frequency_hz = f_ck;
        cfg.target_baud = target_baud;
        cfg.over8 = over8;

        if (!over8) {
            auto mantissa = static_cast<uint32_t>(usartdiv);
            const double frac_part = usartdiv - static_cast<double>(mantissa);
            auto fraction = static_cast<uint32_t>(std::round(frac_part * 16.0));

            if (fraction >= 16) {
                mantissa += 1;
                fraction = 0;
            }

            cfg.mantissa = static_cast<uint16_t>(mantissa);
            cfg.fraction = static_cast<uint8_t>(fraction);
            cfg.brr_value = static_cast<uint16_t>((mantissa << 4) | (fraction & 0x0F));

            const double real_div = static_cast<double>(mantissa) + (static_cast<double>(fraction) / 16.0);
            cfg.real_baud = static_cast<uint32_t>(std::round(static_cast<double>(f_ck) / (16.0 * real_div)));
        } else {
            auto mantissa = static_cast<uint32_t>(usartdiv);
            const double frac_part = usartdiv - static_cast<double>(mantissa);
            auto fraction = static_cast<uint32_t>(std::round(frac_part * 8.0));

            if (fraction >= 8) {
                mantissa += 1;
                fraction = 0;
            }

            cfg.mantissa = static_cast<uint16_t>(mantissa);
            cfg.fraction = static_cast<uint8_t>(fraction);
            cfg.brr_value = static_cast<uint16_t>((mantissa << 4) | (fraction & 0x07));

            const double real_div = static_cast<double>(mantissa) + (static_cast<double>(fraction) / 8.0);
            cfg.real_baud = static_cast<uint32_t>(std::round(static_cast<double>(f_ck) / (8.0 * real_div)));
        }

        cfg.error_percent = (static_cast<double>(cfg.real_baud) - static_cast<double>(target_baud)) /
                            static_cast<double>(target_baud) * 100.0;
        return cfg;
    }

    [[nodiscard]] static std::optional<NxpLpcBrrConfig> calculate_nxp_lpc(
        uint32_t f_pclk, uint32_t target_baud) noexcept
    {
        if (f_pclk == 0 || target_baud == 0) return std::nullopt;

        NxpLpcBrrConfig best{};
        best.bus_frequency_hz = f_pclk;
        best.target_baud = target_baud;
        double min_error = 1e9;

        for (uint32_t mul = 1; mul <= 15; ++mul) {
            for (uint32_t divadd = 0; divadd < mul; ++divadd) {
                const double fr_mult = 1.0 + (static_cast<double>(divadd) / static_cast<double>(mul));
                const double ideal_dl = static_cast<double>(f_pclk) / (16.0 * static_cast<double>(target_baud) * fr_mult);
                const auto dl = static_cast<uint32_t>(std::round(ideal_dl));

                if (dl < 1 || dl > 65535) continue;

                const double real_baud = static_cast<double>(f_pclk) / (16.0 * static_cast<double>(dl) * fr_mult);
                const double err = std::abs((real_baud - static_cast<double>(target_baud)) / static_cast<double>(target_baud) * 100.0);

                if (err < min_error) {
                    min_error = err;
                    best.dll_dlm = static_cast<uint16_t>(dl);
                    best.divaddval = static_cast<uint8_t>(divadd);
                    best.mulval = static_cast<uint8_t>(mul);
                    best.real_baud = static_cast<uint32_t>(std::round(real_baud));
                    best.error_percent = (real_baud - static_cast<double>(target_baud)) / static_cast<double>(target_baud) * 100.0;
                }
            }
        }

        if (min_error < 1e8) return best;
        return std::nullopt;
    }
};

/* Клас потактового симулятора апаратного приймача */
class HardwareReceiverSimulator {
public:
    static bool simulate_frame_reception(
        uint32_t f_ck, uint32_t target_baud, uint16_t mantissa, uint8_t fraction, uint8_t mod = 16)
    {
        uint32_t accumulator = 0;
        uint32_t total_clock_ticks = 0;
        const double bit_period_ideal_ticks = static_cast<double>(f_ck) / static_cast<double>(target_baud);

        std::cout << "  [C++ Емуляція кадру 8-N-1: f_ck=" << f_ck << " Гц, ціль=" << target_baud
                  << " бод, N=" << mantissa << ", F=" << static_cast<int>(fraction) << "/" << static_cast<int>(mod) << "]\n";

        for (uint32_t bit = 0; bit < 10; ++bit) {
            const double bit_start_ideal = static_cast<double>(bit) * bit_period_ideal_ticks;
            const double bit_center_ideal = bit_start_ideal + 0.5 * bit_period_ideal_ticks;
            uint32_t sample_8_tick = 0;

            for (uint32_t sample = 0; sample < 16; ++sample) {
                accumulator += fraction;
                uint32_t step = mantissa;
                if (accumulator >= mod) {
                    accumulator -= mod;
                    step += 1;
                }
                total_clock_ticks += step;
                if (sample == 8) sample_8_tick = total_clock_ticks;
            }

            const double phase_error_ticks = static_cast<double>(sample_8_tick) -
                                             (bit_start_ideal + 8.5 * (bit_period_ideal_ticks / 16.0));
            const double phase_error_fraction = phase_error_ticks / bit_period_ideal_ticks;

            std::cout << "    Біт " << std::setw(2) << bit
                      << ": ідеал_центр=" << std::setw(8) << std::fixed << std::setprecision(1) << bit_center_ideal
                      << ", строб8=" << std::setw(8) << sample_8_tick
                      << ", зсув=" << std::showpos << std::setprecision(3) << phase_error_fraction
                      << std::noshowpos << " біта\n";

            if (std::abs(phase_error_fraction) > 0.40) {
                std::cout << "    [!] ПОМИЛКА КАДРУ: строб вийшов за безпечне вікно!\n";
                return false;
            }
        }
        std::cout << "    [✓] Успішно: усі строби знаходяться глибоко всередині бітів.\n";
        return true;
    }
};

} // namespace uart

int main() {
    std::cout << "=== C++ КАЛЬКУЛЯТОР ДРОБОВИХ ДІЛЬНИКІВ BAUD RATE ===\n\n";

    constexpr uint32_t apb1_clock = 42'000'000;
    constexpr uint32_t target_baud = 921'600;

    const auto cfg16 = uart::BaudRateCalculator::calculate_stm32(apb1_clock, target_baud, false);
    if (cfg16) {
        std::cout << "1. STM32 [OVER8=0, 16x]: BRR=0x" << std::hex << std::uppercase << std::setw(4) << std::setfill('0')
                  << cfg16->brr_value << std::dec << " (N=" << cfg16->mantissa << ", F=" << static_cast<int>(cfg16->fraction)
                  << "/16) -> " << cfg16->real_baud << " бод, похибка=" << std::showpos << std::fixed
                  << std::setprecision(2) << cfg16->error_percent << std::noshowpos << "%\n";
    }

    const auto cfg8 = uart::BaudRateCalculator::calculate_stm32(apb1_clock, target_baud, true);
    if (cfg8) {
        std::cout << "2. STM32 [OVER8=1,  8x]: BRR=0x" << std::hex << std::uppercase << std::setw(4) << std::setfill('0')
                  << cfg8->brr_value << std::dec << " (N=" << cfg8->mantissa << ", F=" << static_cast<int>(cfg8->fraction)
                  << "/8)  -> " << cfg8->real_baud << " бод, похибка=" << std::showpos << std::fixed
                  << std::setprecision(2) << cfg8->error_percent << std::noshowpos << "%\n\n";
    }

    if (cfg16) {
        uart::HardwareReceiverSimulator::simulate_frame_reception(
            apb1_clock, target_baud, cfg16->mantissa, cfg16->fraction, 16);
    }

    return 0;
}
