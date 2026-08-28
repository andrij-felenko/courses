#include <cstdint>
#include <cstddef>
#include <array>
#include <span>
#include <expected>
#include <chrono>

namespace sensor {

enum class Error : uint8_t {
    I2cWriteFailed,
    I2cReadFailed,
    TemperatureCrcMismatch,
    HumidityCrcMismatch
};

struct Reading {
    float temperature_c;
    float humidity_rh;
};

// Концепт або функціональний інтерфейс апаратного драйвера
template <typename I2cBus, typename DelayProvider>
class Sht3x {
public:
    constexpr Sht3x(I2cBus& bus, DelayProvider& delayer, uint8_t addr = 0x44) noexcept
        : bus_(bus), delayer_(delayer), address_(addr) {}

    [[nodiscard]] std::expected<Reading, Error> read_measurement() noexcept {
        // 1. Відправка 16-бітної команди
        constexpr std::array<uint8_t, 2> cmd{0x24, 0x00};
        if (!bus_.write(address_, cmd)) {
            return std::unexpected(Error::I2cWriteFailed);
        }

        // 2. Очікування перетворення
        delayer_.delay(std::chrono::milliseconds(15));

        // 3. Зчитування 6 байтів
        std::array<uint8_t, 6> raw_buf{};
        if (!bus_.read(address_, raw_buf)) {
            return std::unexpected(Error::I2cReadFailed);
        }

        // 4. Перевірка CRC температури
        std::span<const uint8_t, 2> temp_bytes{raw_buf.data(), 2};
        if (calculate_crc(temp_bytes) != raw_buf[2]) {
            return std::unexpected(Error::TemperatureCrcMismatch);
        }

        // 5. Перевірка CRC вологості
        std::span<const uint8_t, 2> humi_bytes{raw_buf.data() + 3, 2};
        if (calculate_crc(humi_bytes) != raw_buf[5]) {
            return std::unexpected(Error::HumidityCrcMismatch);
        }

        // 6. Перерахунок
        const uint16_t raw_t = static_cast<uint16_t>((raw_buf[0] << 8) | raw_buf[1]);
        const uint16_t raw_h = static_cast<uint16_t>((raw_buf[3] << 8) | raw_buf[4]);

        return Reading{
            .temperature_c = -45.0f + 175.0f * (static_cast<float>(raw_t) / 65535.0f),
            .humidity_rh   = 100.0f * (static_cast<float>(raw_h) / 65535.0f)
        };
    }

private:
    [[nodiscard]] static constexpr uint8_t calculate_crc(std::span<const uint8_t> data) noexcept {
        uint8_t crc = 0xFF;
        for (const uint8_t b : data) {
            crc ^= b;
            for (int bit = 0; bit < 8; ++bit) {
                crc = (crc & 0x80) ? static_cast<uint8_t>((crc << 1) ^ 0x31)
                                   : static_cast<uint8_t>(crc << 1);
            }
        }
        return crc;
    }

    I2cBus& bus_;
    DelayProvider& delayer_;
    uint8_t address_;
};

} // namespace sensor
