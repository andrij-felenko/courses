#include <cstdint>
#include <cstddef>
#include <expected>
#include <array>
#include <chrono>
#include <thread>

namespace hardware {

enum class MagnetometerError {
    BusError,
    DeviceNotFound,
    Timeout,
    InvalidConfiguration
};

struct MagneticVector {
    float x_gauss{0.0f};
    float y_gauss{0.0f};
    float z_gauss{0.0f};

    [[nodiscard]] constexpr float toTesla(float gauss) noexcept {
        return gauss * 1e-4f;
    }
};

// Контракт HAL-інтерфейсу I2C шини
class II2CBus {
public:
    virtual ~II2CBus() = default;
    virtual std::expected<void, MagnetometerError> writeRegister(uint8_t dev_addr, uint8_t reg_addr, uint8_t value) noexcept = 0;
    virtual std::expected<void, MagnetometerError> readRegisters(uint8_t dev_addr, uint8_t reg_addr, std::span<uint8_t> out_buffer) noexcept = 0;
};

class MMC5983MA {
public:
    static constexpr uint8_t I2C_ADDR = 0x30;
    static constexpr uint8_t EXPECTED_ID = 0x30;

    explicit MMC5983MA(II2CBus& bus) noexcept : bus_(bus) {}

    std::expected<void, MagnetometerError> init() noexcept {
        // Програмне скидання
        auto res = bus_.writeRegister(I2C_ADDR, 0x08, 0x80);
        if (!res) return res;

        std::this_thread::sleep_for(std::chrono::milliseconds(15));

        // Перевірка ID
        std::array<uint8_t, 1> id_buf{};
        res = bus_.readRegisters(I2C_ADDR, 0x2F, id_buf);
        if (!res) return res;
        if (id_buf[0] != EXPECTED_ID) {
            return std::unexpected(MagnetometerError::DeviceNotFound);
        }

        // Конфігурація: 18 біт (BW = 100 Гц) + авто SET/RESET
        res = bus_.writeRegister(I2C_ADDR, 0x09, 0x03);
        if (!res) return res;

        return bus_.writeRegister(I2C_ADDR, 0x08, 0x20);
    }

    std::expected<void, MagnetometerError> degaussPulse() noexcept {
        auto res = bus_.writeRegister(I2C_ADDR, 0x08, 0x08); // SET
        if (!res) return res;
        std::this_thread::sleep_for(std::chrono::milliseconds(1));

        res = bus_.writeRegister(I2C_ADDR, 0x08, 0x10); // RESET
        if (!res) return res;
        std::this_thread::sleep_for(std::chrono::milliseconds(1));

        return bus_.writeRegister(I2C_ADDR, 0x08, 0x20); // Відновлення Auto SR
    }

    std::expected<MagneticVector, MagnetometerError> readMeasurement() noexcept {
        // Запуск вимірювання
        auto res = bus_.writeRegister(I2C_ADDR, 0x08, 0x21);
        if (!res) return std::unexpected(res.error());

        // Очікування готовності Data Ready
        bool ready = false;
        for (int i = 0; i < 50; ++i) {
            std::array<uint8_t, 1> st{};
            if (bus_.readRegisters(I2C_ADDR, 0x07, st)) {
                if (st[0] & 0x01) {
                    ready = true;
                    break;
                }
            }
            std::this_thread::sleep_for(std::chrono::milliseconds(1));
        }

        if (!ready) {
            return std::unexpected(MagnetometerError::Timeout);
        }

        std::array<uint8_t, 7> raw{};
        res = bus_.readRegisters(I2C_ADDR, 0x00, raw);
        if (!res) return std::unexpected(res.error());

        const uint32_t raw_x = (static_cast<uint32_t>(raw[0]) << 10) | (static_cast<uint32_t>(raw[1]) << 2) | ((raw[6] >> 6) & 0x03);
        const uint32_t raw_y = (static_cast<uint32_t>(raw[2]) << 10) | (static_cast<uint32_t>(raw[3]) << 2) | ((raw[6] >> 4) & 0x03);
        const uint32_t raw_z = (static_cast<uint32_t>(raw[4]) << 10) | (static_cast<uint32_t>(raw[5]) << 2) | ((raw[6] >> 2) & 0x03);

        MagneticVector vec{
            .x_gauss = (static_cast<float>(raw_x) - 131072.0f) / 16384.0f,
            .y_gauss = (static_cast<float>(raw_y) - 131072.0f) / 16384.0f,
            .z_gauss = (static_cast<float>(raw_z) - 131072.0f) / 16384.0f
        };

        return vec;
    }

private:
    II2CBus& bus_;
};

} // namespace hardware
