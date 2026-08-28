#include <iostream>
#include <vector>
#include <array>
#include <span>
#include <random>
#include <cmath>
#include <iomanip>
#include <cstdint>
#include <bit>

namespace pam4 {

// Номінальні рівні напруги PAM4: L0=-3.0, L1=-1.0, L2=+1.0, L3=+3.0
constexpr std::array<double, 4> VOLTAGE_LEVELS = { -3.0, -1.0, 1.0, 3.0 };

// Таблиці перетворення дибітів у номери рівнів і навпаки
constexpr std::array<uint8_t, 4> GRAY_MAP     = { 0, 1, 3, 2 }; // 00->L0, 01->L1, 10->L3, 11->L2
constexpr std::array<uint8_t, 4> GRAY_DEMAP   = { 0, 1, 3, 2 };
constexpr std::array<uint8_t, 4> BINARY_MAP   = { 0, 1, 2, 3 };
constexpr std::array<uint8_t, 4> BINARY_DEMAP = { 0, 1, 2, 3 };

// Трипороговий слайсер: квантування напруги
[[nodiscard]] constexpr uint8_t slice(double voltage) noexcept
{
    if (voltage < -2.0) return 0; // L0 (-3 В)
    if (voltage < 0.0)  return 1; // L1 (-1 В)
    if (voltage < 2.0)  return 2; // L2 (+1 В)
    return 3;                     // L3 (+3 В)
}

// Підрахунок відстані Геммінга через стандартний std::popcount
[[nodiscard]] constexpr uint32_t bit_distance(uint8_t a, uint8_t b) noexcept
{
    return static_cast<uint32_t>(std::popcount(static_cast<unsigned>(a ^ b)));
}

// Структура накопичення метрик якості каналу
struct ChannelMetrics {
    double snr_db{0.0};
    uint64_t total_symbols{0};
    uint64_t sym_errors_gray{0};
    uint64_t bit_errors_gray{0};
    uint64_t sym_errors_bin{0};
    uint64_t bit_errors_bin{0};

    [[nodiscard]] double ser_gray() const noexcept {
        return static_cast<double>(sym_errors_gray) / static_cast<double>(total_symbols);
    }
    [[nodiscard]] double ber_gray() const noexcept {
        return static_cast<double>(bit_errors_gray) / static_cast<double>(2 * total_symbols);
    }
    [[nodiscard]] double ber_bin() const noexcept {
        return static_cast<double>(bit_errors_bin) / static_cast<double>(2 * total_symbols);
    }
    [[nodiscard]] double gray_factor() const noexcept {
        return (ber_gray() > 0.0) ? (ber_bin() / ber_gray()) : 1.0;
    }
};

// Об'єктний симулятор тракту передачі
class Pam4Simulator {
public:
    explicit Pam4Simulator(uint64_t seed = std::random_device{}())
        : rng_(seed), dibit_dist_(0, 3) {}

    ChannelMetrics run_simulation(double snr_db, uint64_t num_symbols)
    {
        ChannelMetrics metrics{ .snr_db = snr_db, .total_symbols = num_symbols };

        // Середня енергія символу Es = 5.0
        constexpr double es = 5.0;
        const double snr_linear = std::pow(10.0, snr_db / 10.0);
        const double sigma = std::sqrt(es / (2.0 * snr_linear));

        std::normal_distribution<double> noise_dist(0.0, sigma);

        for (uint64_t i = 0; i < num_symbols; ++i) {
            const uint8_t tx_bits = static_cast<uint8_t>(dibit_dist_(rng_));

            // 1. Потік із кодуванням Грея
            const uint8_t lvl_gray = GRAY_MAP[tx_bits];
            const double tx_v_gray = VOLTAGE_LEVELS[lvl_gray];
            const double rx_v_gray = tx_v_gray + noise_dist(rng_);
            const uint8_t rx_lvl_gray = slice(rx_v_gray);
            const uint8_t rx_bits_gray = GRAY_DEMAP[rx_lvl_gray];

            if (rx_lvl_gray != lvl_gray) {
                metrics.sym_errors_gray++;
                metrics.bit_errors_gray += bit_distance(tx_bits, rx_bits_gray);
            }

            // 2. Потік із натуральним двійковим кодуванням
            const uint8_t lvl_bin = BINARY_MAP[tx_bits];
            const double tx_v_bin = VOLTAGE_LEVELS[lvl_bin];
            const double rx_v_bin = tx_v_bin + noise_dist(rng_);
            const uint8_t rx_lvl_bin = slice(rx_v_bin);
            const uint8_t rx_bits_bin = BINARY_DEMAP[rx_lvl_bin];

            if (rx_lvl_bin != lvl_bin) {
                metrics.sym_errors_bin++;
                metrics.bit_errors_bin += bit_distance(tx_bits, rx_bits_bin);
            }
        }

        return metrics;
    }

private:
    std::mt19937_64 rng_;
    std::uniform_int_distribution<int> dibit_dist_;
};

} // namespace pam4

int main()
{
    constexpr uint64_t SYMBOLS = 2'000'000;
    const std::vector<double> snr_scan = { 10.0, 12.0, 14.0, 16.0, 18.0, 20.0 };

    pam4::Pam4Simulator simulator(42);

    std::cout << "=== Симуляція тракту PAM4 SerDes у каналі AWGN (C++) ===\n";
    std::cout << "Обсяг вибірки на точку: " << SYMBOLS << " символів (4.00 млн бітів)\n\n";
    std::cout << std::setw(8)  << "SNR (дБ)" << " | "
              << std::setw(12) << "SER (Gray)" << " | "
              << std::setw(12) << "BER (Gray)" << " | "
              << std::setw(12) << "BER (Binary)" << " | "
              << std::setw(16) << "BER_Bin/BER_Gray" << "\n";
    std::cout << std::string(72, '-') << "\n";

    for (double snr : snr_scan) {
        auto metrics = simulator.run_simulation(snr, SYMBOLS);
        std::cout << std::fixed << std::setprecision(1) << std::setw(8) << metrics.snr_db << " | "
                  << std::scientific << std::setprecision(4)
                  << std::setw(12) << metrics.ser_gray() << " | "
                  << std::setw(12) << metrics.ber_gray() << " | "
                  << std::setw(12) << metrics.ber_bin() << " | "
                  << std::fixed << std::setprecision(3)
                  << std::setw(16) << metrics.gray_factor() << "\n";
    }

    return 0;
}
