#include <cstdint>
#include <array>
#include <cmath>
#include <expected>
#include <numbers>

namespace hardware {

enum class MagnetoError {
    I2cCommunicationFailed,
    DeviceNotFound,
    NotInitialized,
    InvalidParameter
};

struct Vector3f {
    float x{0.0f};
    float y{0.0f};
    float z{0.0f};

    [[nodiscard]] constexpr float magnitude() const noexcept {
        return std::sqrt(x * x + y * y + z * z);
    }
};

struct MagnetoCalibration {
    Vector3f offset{0.0f, 0.0f, 0.0f};
    Vector3f scale{1.0f, 1.0f, 1.0f};
};

class MagnetometerDriver {
public:
    explicit MagnetometerDriver(uint8_t i2c_address) noexcept
        : i2c_addr_(i2c_address) {}

    [[nodiscard]] std::expected<void, MagnetoError> initialize() noexcept {
        uint8_t who_am_i = 0;
        if (!i2c_read_reg(0x0F, who_am_i)) {
            return std::unexpected(MagnetoError::I2cCommunicationFailed);
        }

        if (who_am_i != 0x3D) {
            return std::unexpected(MagnetoError::DeviceNotFound);
        }

        // CTRL_REG1..3 setup
        if (!i2c_write_reg(0x20, 0x70) || 
            !i2c_write_reg(0x21, 0x00) || 
            !i2c_write_reg(0x22, 0x00)) {
            return std::unexpected(MagnetoError::I2cCommunicationFailed);
        }

        initialized_ = true;
        return {};
    }

    [[nodiscard]] std::expected<Vector3f, MagnetoError> read_magnetic_field_uT() const noexcept {
        if (!initialized_) {
            return std::unexpected(MagnetoError::NotInitialized);
        }

        std::array<uint8_t, 6> raw_buf{};
        if (!i2c_read_bytes(0x28 | 0x80, raw_buf.data(), raw_buf.size())) {
            return std::unexpected(MagnetoError::I2cCommunicationFailed);
        }

        const auto raw_x = static_cast<int16_t>((raw_buf[1] << 8) | raw_buf[0]);
        const auto raw_y = static_cast<int16_t>((raw_buf[3] << 8) | raw_buf[2]);
        const auto raw_z = static_cast<int16_t>((raw_buf[5] << 8) | raw_buf[4]);

        constexpr float lsb_to_uT = (1.0f / 6842.0f) * 100.0f;
        Vector3f raw_uT{
            static_cast<float>(raw_x) * lsb_to_uT,
            static_cast<float>(raw_y) * lsb_to_uT,
            static_cast<float>(raw_z) * lsb_to_uT
        };

        return Vector3f{
            (raw_uT.x - calib_.offset.x) * calib_.scale.x,
            (raw_uT.y - calib_.offset.y) * calib_.scale.y,
            (raw_uT.z - calib_.offset.z) * calib_.scale.z
        };
    }

    void set_calibration(const MagnetoCalibration& calib) noexcept {
        calib_ = calib;
    }

    [[nodiscard]] static float estimate_dipole_moment(float field_bz_uT, float distance_m) noexcept {
        const float B_z_tesla = field_bz_uT * 1e-6f;
        const float r3 = std::pow(distance_m, 3.0f);
        constexpr float mu_0 = 1.256637e-6f;

        return (2.0f * std::numbers::pi_v<float> * r3 * B_z_tesla) / mu_0;
    }

private:
    uint8_t i2c_addr_;
    bool initialized_{false};
    MagnetoCalibration calib_{};

    // Заглушки платформних функцій I2C
    bool i2c_read_reg(uint8_t reg, uint8_t& val) const noexcept { return true; }
    bool i2c_write_reg(uint8_t reg, uint8_t val) const noexcept { return true; }
    bool i2c_read_bytes(uint8_t reg, uint8_t* dst, size_t len) const noexcept { return true; }
};

} // namespace hardware
