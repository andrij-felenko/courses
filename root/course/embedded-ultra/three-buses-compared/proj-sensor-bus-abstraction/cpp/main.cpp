/* ============================================================================
 * bus_hal.hpp — Уніфікований шар шин автопілота на ідіоматичному C++20
 * ============================================================================ */
#include <cstdint>
#include <cstddef>
#include <span>
#include <array>
#include <expected>
#include <concepts>

namespace avionics {

enum class BusError : uint8_t {
    Timeout,
    Nack,
    ArbitrationLost,
    InvalidParam,
    Busy
};

/* Контракт абстрактного пристрою на довільній послідовній шині */
class IBusDevice {
public:
    virtual ~IBusDevice() = default;
    virtual std::expected<void, BusError> write_reg(uint8_t reg, std::span<const uint8_t> data) = 0;
    virtual std::expected<void, BusError> read_reg(uint8_t reg, std::span<uint8_t> data) = 0;
    virtual std::expected<void, BusError> transfer(std::span<const uint8_t> tx, std::span<uint8_t> rx) = 0;
};

/* Апаратні функції платформи */
extern void gpio_pin_write(uint32_t pin, bool level);
extern std::expected<void, BusError> spi_hw_xfer(void* inst, std::span<const uint8_t> tx, std::span<uint8_t> rx);
extern std::expected<void, BusError> i2c_hw_write(void* inst, uint8_t addr, uint8_t reg, std::span<const uint8_t> data);
extern std::expected<void, BusError> i2c_hw_read(void* inst, uint8_t addr, uint8_t reg, std::span<uint8_t> data);
extern void i2c_hw_recover();

/* RAII-обгортка для автоматичного керування вибором мікросхеми CS */
class ChipSelectGuard {
public:
    explicit ChipSelectGuard(uint32_t cs_pin) noexcept : cs_pin_(cs_pin) {
        gpio_pin_write(cs_pin_, false); /* CS Active LOW */
    }
    ~ChipSelectGuard() noexcept {
        gpio_pin_write(cs_pin_, true);  /* CS High (Idle) */
    }
    ChipSelectGuard(const ChipSelectGuard&) = delete;
    ChipSelectGuard& operator=(const ChipSelectGuard&) = delete;

private:
    uint32_t cs_pin_;
};

/* Реалізація для пристрою на шині SPI */
class SpiBusDevice final : public IBusDevice {
public:
    constexpr SpiBusDevice(void* spi_inst, uint32_t cs_pin) noexcept
        : spi_inst_(spi_inst), cs_pin_(cs_pin) {
        gpio_pin_write(cs_pin_, true);
    }

    std::expected<void, BusError> write_reg(uint8_t reg, std::span<const uint8_t> data) override {
        ChipSelectGuard cs(cs_pin_);
        uint8_t reg_header = reg & 0x7FU;
        auto res = spi_hw_xfer(spi_inst_, std::span(&reg_header, 1), {});
        if (!res) return res;
        if (!data.empty()) {
            return spi_hw_xfer(spi_inst_, data, {});
        }
        return {};
    }

    std::expected<void, BusError> read_reg(uint8_t reg, std::span<uint8_t> data) override {
        ChipSelectGuard cs(cs_pin_);
        uint8_t reg_header = reg | 0x80U;
        auto res = spi_hw_xfer(spi_inst_, std::span(&reg_header, 1), {});
        if (!res) return res;
        if (!data.empty()) {
            return spi_hw_xfer(spi_inst_, {}, data);
        }
        return {};
    }

    std::expected<void, BusError> transfer(std::span<const uint8_t> tx, std::span<uint8_t> rx) override {
        ChipSelectGuard cs(cs_pin_);
        return spi_hw_xfer(spi_inst_, tx, rx);
    }

private:
    void* spi_inst_;
    uint32_t cs_pin_;
};

/* Реалізація для пристрою на шині I2C */
class I2cBusDevice final : public IBusDevice {
public:
    constexpr I2cBusDevice(void* i2c_inst, uint8_t addr_7bit) noexcept
        : i2c_inst_(i2c_inst), addr_7bit_(addr_7bit) {}

    std::expected<void, BusError> write_reg(uint8_t reg, std::span<const uint8_t> data) override {
        auto res = i2c_hw_write(i2c_inst_, addr_7bit_, reg, data);
        if (!res && res.error() == BusError::Timeout) {
            i2c_hw_recover();
        }
        return res;
    }

    std::expected<void, BusError> read_reg(uint8_t reg, std::span<uint8_t> data) override {
        auto res = i2c_hw_read(i2c_inst_, addr_7bit_, reg, data);
        if (!res && res.error() == BusError::Timeout) {
            i2c_hw_recover();
        }
        return res;
    }

    std::expected<void, BusError> transfer(std::span<const uint8_t>, std::span<uint8_t>) override {
        return std::unexpected(BusError::InvalidParam);
    }

private:
    void* i2c_inst_;
    uint8_t addr_7bit_;
};

/* Типізований драйвер IMU-сенсора */
struct ImuSample {
    float accel_x, accel_y, accel_z; /* у м/с² */
    float gyro_x,  gyro_y,  gyro_z;  /* у рад/с */
    float temp_c;                    /* у °C */
};

class Icm42688Driver {
public:
    explicit constexpr Icm42688Driver(IBusDevice& bus) noexcept : bus_(bus) {}

    std::expected<ImuSample, BusError> read_sensor() {
        std::array<uint8_t, 14> raw{};
        auto res = bus_.read_reg(0x1F, raw);
        if (!res) return std::unexpected(res.error());

        auto parse_i16 = [](uint8_t msb, uint8_t lsb) -> int16_t {
            return static_cast<int16_t>((static_cast<uint16_t>(msb) << 8) | lsb);
        };

        constexpr float ACCEL_SCALE = 9.80665f / 2048.0f; /* ±16g */
        constexpr float GYRO_SCALE  = 0.0174532925f / 16.4f; /* ±2000 dps */

        return ImuSample{
            .accel_x = parse_i16(raw[0],  raw[1])  * ACCEL_SCALE,
            .accel_y = parse_i16(raw[2],  raw[3])  * ACCEL_SCALE,
            .accel_z = parse_i16(raw[4],  raw[5])  * ACCEL_SCALE,
            .gyro_x  = parse_i16(raw[6],  raw[7])  * GYRO_SCALE,
            .gyro_y  = parse_i16(raw[8],  raw[9])  * GYRO_SCALE,
            .gyro_z  = parse_i16(raw[10], raw[11]) * GYRO_SCALE,
            .temp_c  = parse_i16(raw[12], raw[13]) / 132.48f + 25.0f
        };
    }

private:
    IBusDevice& bus_;
};

} // namespace avionics
