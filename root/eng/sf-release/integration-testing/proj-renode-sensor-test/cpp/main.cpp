#include <cstdint>
#include <cstddef>
#include <span>
#include <expected>
#include <chrono>

namespace embedded::sensors {

inline constexpr uint8_t  kSensorI2cAddr    = (0x44 << 1);
inline constexpr uint16_t kSensorCmdMeasure = 0x2C06;
inline constexpr uint8_t  kCrc8Polynomial   = 0x31;
inline constexpr uint8_t  kCrc8Init         = 0xFF;
inline constexpr int      kMaxRetryCount    = 3;
inline constexpr uint32_t kI2cTimeoutCycles = 50000;

enum class SensorError : uint8_t {
    BusFault,
    CrcMismatch,
    Timeout
};

class TemperatureSensor {
public:
    static constexpr uint8_t CalculateCrc8(std::span<const uint8_t> data) noexcept {
        uint8_t crc = kCrc8Init;
        for (uint8_t byte : data) {
            crc ^= byte;
            for (int bit = 0; bit < 8; ++bit) {
                if ((crc & 0x80) != 0) {
                    crc = static_cast<uint8_t>((crc << 1) ^ kCrc8Polynomial);
                } else {
                    crc = static_cast<uint8_t>(crc << 1);
                }
            }
        }
        return crc;
    }

    static std::expected<float, SensorError> ReadTemperature() noexcept {
        const uint8_t cmd[2] = {
            static_cast<uint8_t>(kSensorCmdMeasure >> 8),
            static_cast<uint8_t>(kSensorCmdMeasure & 0xFF)
        };
        uint8_t rx_buf[3] = { 0 };

        for (int attempt = 0; attempt < kMaxRetryCount; ++attempt) {
            if (!HalI2cWrite(kSensorI2cAddr, cmd, sizeof(cmd), kI2cTimeoutCycles)) {
                HalI2cBusRecover9Clocks();
                continue;
            }

            if (!HalI2cRead(kSensorI2cAddr, rx_buf, sizeof(rx_buf), kI2cTimeoutCycles)) {
                HalI2cBusRecover9Clocks();
                continue;
            }

            const uint8_t calculated_crc = CalculateCrc8(std::span<const uint8_t>(rx_buf, 2));
            if (calculated_crc != rx_buf[2]) {
                continue;
            }

            const uint16_t raw_val = static_cast<uint16_t>((rx_buf[0] << 8) | rx_buf[1]);
            const float temp = -45.0f + 175.0f * (static_cast<float>(raw_val) / 65535.0f);
            return temp;
        }

        return std::unexpected(SensorError::CrcMismatch);
    }

private:
    static bool HalI2cWrite(uint8_t addr, const uint8_t *data, size_t len, uint32_t timeout) noexcept;
    static bool HalI2cRead(uint8_t addr, uint8_t *data, size_t len, uint32_t timeout) noexcept;
    static void HalI2cBusRecover9Clocks() noexcept;
};

} // namespace embedded::sensors
