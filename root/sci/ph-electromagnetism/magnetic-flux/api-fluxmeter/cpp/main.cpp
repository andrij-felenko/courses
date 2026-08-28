#include <cstdint>
#include <array>
#include <span>
#include <expected>
#include <concepts>

template <typename I2CInterface>
class Fluxmeter {
public:
    enum class Error {
        CommunicationFailed,
        CalibrationTimeout,
        InvalidArguments,
        HardwareSaturation
    };

    struct Config {
        uint8_t i2c_address{0x48};
        double lsb_to_weber{1.19209289e-7}; /* 2.0 Vb / 2^23 LSB */
    };

    explicit Fluxmeter(I2CInterface& bus, Config cfg = {}) noexcept
        : bus_(bus), config_(cfg) {}

    [[nodiscard]] std::expected<void, Error> init() noexcept {
        constexpr uint8_t ctrl_val = 0x01; // ENABLE
        if (!bus_.write(config_.i2c_address, 0x00, std::span{&ctrl_val, 1})) {
            return std::unexpected(Error::CommunicationFailed);
        }
        return {};
    }

    [[nodiscard]] std::expected<void, Error> calibrate_zero() noexcept {
        constexpr uint8_t ctrl_val = 0x03; // ENABLE | AUTO_ZERO
        if (!bus_.write(config_.i2c_address, 0x00, std::span{&ctrl_val, 1})) {
            return std::unexpected(Error::CommunicationFailed);
        }

        uint8_t status = 0;
        std::size_t retries = 100;
        while (retries-- > 0) {
            if (bus_.read(config_.i2c_address, 0x02, std::span{&status, 1})) {
                if (status & 0x04) { // CAL_DONE
                    return {};
                }
            }
            bus_.delay_ms(10);
        }
        return std::unexpected(Error::CalibrationTimeout);
    }

    [[nodiscard]] std::expected<double, Error> read_flux() noexcept {
        std::array<uint8_t, 3> buf{};
        if (!bus_.read(config_.i2c_address, 0x03, std::span{buf})) {
            return std::unexpected(Error::CommunicationFailed);
        }

        int32_t raw_adc = static_cast<int32_t>(buf[0] | (buf[1] << 8) | (buf[2] << 16));
        if (raw_adc & 0x00800000) {
            raw_adc |= 0xFF000000; // Sign extend
        }

        return static_cast<double>(raw_adc) * config_.lsb_to_weber;
    }

private:
    I2CInterface& bus_;
    Config config_;
};
