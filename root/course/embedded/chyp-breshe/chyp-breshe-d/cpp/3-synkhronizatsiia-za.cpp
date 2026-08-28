#include <cstdint>
#include <array>
#include <optional>

struct AccelAxes {
    int16_t x{};
    int16_t y{};
    int16_t z{};
};

class SensorDriver {
public:
    static constexpr uint8_t REG_OUT_X_L  = 0x28;
    static constexpr uint8_t I2C_AUTO_INC = 0x80;

    // Повертає когерентні осі або std::nullopt при апаратній помилці
    std::optional<AccelAxes> read_accel_atomic(uint8_t dev_addr) noexcept {
        std::array<uint8_t, 6> raw_buf{};
        const uint8_t start_reg = REG_OUT_X_L | I2C_AUTO_INC;

        if (!i2c_transfer(dev_addr, start_reg, raw_buf)) {
            return std::nullopt;
        }

        return AccelAxes{
            .x = static_cast<int16_t>((static_cast<uint16_t>(raw_buf[1]) << 8) | static_cast<uint16_t>(raw_buf[0])),
            .y = static_cast<int16_t>((static_cast<uint16_t>(raw_buf[3]) << 8) | static_cast<uint16_t>(raw_buf[2])),
            .z = static_cast<int16_t>((static_cast<uint16_t>(raw_buf[5] << 8)) | static_cast<uint16_t>(raw_buf[4]))
        };
    }

private:
    bool i2c_transfer(uint8_t addr, uint8_t reg, std::span<uint8_t> rx_buf) noexcept;
};
