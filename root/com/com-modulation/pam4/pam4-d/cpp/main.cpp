#include <iostream>
#include <vector>
#include <array>
#include <span>
#include <random>
#include <cmath>
#include <iomanip>
#include <cstdint>

namespace pam4 {

// Номінальні напруги для 4 рівнів PAM4 (L0..L3)
constexpr std::array<double, 4> VOLTAGES = { -3.0, -1.0, 1.0, 3.0 };

// Таблиці відображення коду Грея для пари бітів
constexpr std::array<uint8_t, 4> GRAY_ENCODER = { 0, 1, 3, 2 }; // 00->L0, 01->L1, 10->L3, 11->L2
constexpr std::array<uint8_t, 4> GRAY_DECODER = { 0, 1, 3, 2 };

// Модулятор: перетворює двійковий дибіт у напругу рівня
[[nodiscard]] constexpr double modulate(uint8_t dibit) noexcept
{
    const uint8_t level_idx = GRAY_ENCODER[dibit & 0x03];
    return VOLTAGES[level_idx];
}

// Трипороговий слайсер
[[nodiscard]] constexpr uint8_t slice(double voltage) noexcept
{
    if (voltage < -2.0) return 0; // L0 (-3 В)
    if (voltage < 0.0)  return 1; // L1 (-1 В)
    if (voltage < 2.0)  return 2; // L2 (+1 В)
    return 3;                     // L3 (+3 В)
}

// Демодулятор: повертає відновлені 2 біти
[[nodiscard]] constexpr uint8_t demodulate(double voltage) noexcept
{
    return GRAY_DECODER[slice(voltage)];
}

// Симулятор фізичного тракту PAM4
class Transceiver {
public:
    explicit Transceiver(double noise_stddev, uint64_t seed = 12345)
        : dist_(0.0, noise_stddev), rng_(seed) {}

    struct ChannelSample {
        uint8_t tx_bits;
        uint8_t tx_level;
        double  tx_voltage;
        double  rx_voltage;
        uint8_t rx_level;
        uint8_t rx_bits;
        bool    success;
    };

    [[nodiscard]] ChannelSample transmit_dibit(uint8_t dibit)
    {
        const uint8_t tx_lvl = GRAY_ENCODER[dibit & 0x03];
        const double tx_v = VOLTAGES[tx_lvl];
        const double rx_v = tx_v + dist_(rng_);
        const uint8_t rx_lvl = slice(rx_v);
        const uint8_t rx_b = GRAY_DECODER[rx_lvl];

        return ChannelSample{
            .tx_bits = dibit,
            .tx_level = tx_lvl,
            .tx_voltage = tx_v,
            .rx_voltage = rx_v,
            .rx_level = rx_lvl,
            .rx_bits = rx_b,
            .success = (dibit == rx_b)
        };
    }

private:
    std::normal_distribution<double> dist_;
    std::mt19937_64 rng_;
};

} // namespace pam4

int main()
{
    constexpr std::array<uint8_t, 4> test_dibits = { 0b00, 0b01, 0b11, 0b10 };
    pam4::Transceiver transceiver(0.35); // рівень шуму sigma = 0.35 В

    std::cout << "=== Демонстрація модулятора та слайсера PAM4 (C++) ===\n\n";
    std::cout << " Вхідні біти | Рівень | Напруга TX | Напруга RX | Зчитано | Вихідні біти | Стан\n";
    std::cout << "-------------+--------+------------+------------+---------+--------------+------\n";

    for (uint8_t dibit : test_dibits) {
        auto sample = transceiver.transmit_dibit(dibit);

        std::cout << "   «" << ((sample.tx_bits >> 1) & 1) << (sample.tx_bits & 1) << "» ("
                  << static_cast<unsigned>(sample.tx_bits) << ")   |   L"
                  << static_cast<unsigned>(sample.tx_level) << "   |  "
                  << std::showpos << std::fixed << std::setprecision(2) << std::setw(6) << sample.tx_voltage << " В  |  "
                  << std::setw(6) << sample.rx_voltage << " В  |   L"
                  << std::noshowpos << static_cast<unsigned>(sample.rx_level) << "   |   «"
                  << ((sample.rx_bits >> 1) & 1) << (sample.rx_bits & 1) << "» ("
                  << static_cast<unsigned>(sample.rx_bits) << ")   |  "
                  << (sample.success ? "OK" : "ПОМИЛКА") << "\n";
    }

    return 0;
}
