#include <cstdint>
#include <array>
#include <span>
#include <optional>
#include <expected>
#include <bit>
#include <functional>

namespace sensirion {

enum class SensorError : uint8_t {
    BusError,
    CrcMismatch,
    NotReady,
    InvalidParameter
};

struct SensorData {
    float co2_ppm{0.0f};
    float temperature_c{0.0f};
    float relative_humidity_pct{0.0f};
};

class Scd30Driver {
public:
    using WriteFn = std::function<bool(uint8_t addr, std::span<const uint8_t> data)>;
    using ReadFn = std::function<bool(uint8_t addr, std::span<uint8_t> data)>;
    using DelayFn = std::function<void(uint32_t ms)>;

    constexpr static uint8_t I2cAddress = 0x61;

    Scd30Driver(WriteFn write, ReadFn read, DelayFn delay)
        : write_fn_{std::move(write)}, read_fn_{std::move(read)}, delay_fn_{std::move(delay)} {}

    [[nodiscard]] std::expected<void, SensorError> start_continuous(uint16_t ambient_pressure_mbar = 0) noexcept {
        return send_command_with_arg(Command::StartContinuous, ambient_pressure_mbar);
    }

    [[nodiscard]] std::expected<void, SensorError> stop_continuous() noexcept {
        return send_simple_command(Command::StopContinuous);
    }

    [[nodiscard]] std::expected<bool, SensorError> is_data_ready() noexcept {
        const auto cmd = static_cast<uint16_t>(Command::GetDataReady);
        const std::array<uint8_t, 2> tx_buf{
            static_cast<uint8_t>(cmd >> 8),
            static_cast<uint8_t>(cmd & 0xFF)
        };

        if (!write_fn_(I2cAddress, tx_buf)) return std::unexpected(SensorError::BusError);
        delay_fn_(3);

        std::array<uint8_t, 3> rx_buf{};
        if (!read_fn_(I2cAddress, rx_buf)) return std::unexpected(SensorError::BusError);
        if (compute_crc(std::span{rx_buf.data(), 2}) != rx_buf[2]) {
            return std::unexpected(SensorError::CrcMismatch);
        }

        const uint16_t status = (static_cast<uint16_t>(rx_buf[0]) << 8) | rx_buf[1];
        return (status == 1);
    }

    [[nodiscard]] std::expected<SensorData, SensorError> read_measurement() noexcept {
        const auto cmd = static_cast<uint16_t>(Command::ReadMeasurement);
        const std::array<uint8_t, 2> tx_buf{
            static_cast<uint8_t>(cmd >> 8),
            static_cast<uint8_t>(cmd & 0xFF)
        };

        if (!write_fn_(I2cAddress, tx_buf)) return std::unexpected(SensorError::BusError);
        delay_fn_(3);

        std::array<uint8_t, 18> rx_buf{};
        if (!read_fn_(I2cAddress, rx_buf)) return std::unexpected(SensorError::BusError);

        for (size_t i = 0; i < 6; ++i) {
            if (compute_crc(std::span{&rx_buf[i * 3], 2}) != rx_buf[i * 3 + 2]) {
                return std::unexpected(SensorError::CrcMismatch);
            }
        }

        const auto unpack_float = [](const uint8_t* p) noexcept -> float {
            const uint32_t raw = (static_cast<uint32_t>(p[0]) << 24) |
                                 (static_cast<uint32_t>(p[1]) << 16) |
                                 (static_cast<uint32_t>(p[3]) << 8)  |
                                 (static_cast<uint32_t>(p[4]));
            return std::bit_cast<float>(raw);
        };

        SensorData data{};
        data.co2_ppm = unpack_float(&rx_buf[0]);
        data.temperature_c = unpack_float(&rx_buf[6]);
        data.relative_humidity_pct = unpack_float(&rx_buf[12]);

        return data;
    }

    [[nodiscard]] std::expected<void, SensorError> set_auto_self_calibration(bool enable) noexcept {
        return send_command_with_arg(Command::SetAutoCalibration, enable ? 1 : 0);
    }

private:
    enum class Command : uint16_t {
        StartContinuous    = 0x0010,
        StopContinuous     = 0x0104,
        SetInterval        = 0x4600,
        GetDataReady       = 0x0202,
        ReadMeasurement    = 0x0300,
        SetAutoCalibration = 0x5306,
        SetForcedRecalib   = 0x5204,
        SoftReset          = 0xD304
    };

    static uint8_t compute_crc(std::span<const uint8_t> data) noexcept {
        uint8_t crc = 0xFF;
        for (uint8_t byte : data) {
            crc ^= byte;
            for (uint8_t b = 0; b < 8; ++b) {
                crc = (crc & 0x80) ? static_cast<uint8_t>((crc << 1) ^ 0x31) : static_cast<uint8_t>(crc << 1);
            }
        }
        return crc;
    }

    std::expected<void, SensorError> send_simple_command(Command cmd) noexcept {
        const auto val = static_cast<uint16_t>(cmd);
        const std::array<uint8_t, 2> buf{
            static_cast<uint8_t>(val >> 8),
            static_cast<uint8_t>(val & 0xFF)
        };
        if (!write_fn_(I2cAddress, buf)) return std::unexpected(SensorError::BusError);
        return {};
    }

    std::expected<void, SensorError> send_command_with_arg(Command cmd, uint16_t arg) noexcept {
        const auto val = static_cast<uint16_t>(cmd);
        std::array<uint8_t, 5> buf{
            static_cast<uint8_t>(val >> 8),
            static_cast<uint8_t>(val & 0xFF),
            static_cast<uint8_t>(arg >> 8),
            static_cast<uint8_t>(arg & 0xFF),
            0
        };
        buf[4] = compute_crc(std::span{&buf[2], 2});
        if (!write_fn_(I2cAddress, buf)) return std::unexpected(SensorError::BusError);
        return {};
    }

    WriteFn write_fn_;
    ReadFn read_fn_;
    DelayFn delay_fn_;
};

} // namespace sensirion
