/* ============================================================================
 * sensor_hal.hpp — Ідіоматичний C++20 інтерфейс шин та драйверів
 * ============================================================================ */
#include <cstdint>
#include <cstddef>
#include <span>
#include <array>
#include <expected>

namespace avionics {

enum class BusStatus : uint8_t {
    Ok = 0,
    Timeout,
    Nack,
    InvalidParameter
};

/* Абстрактний інтерфейс пристрою на шині */
class IBusDevice {
public:
    virtual ~IBusDevice() = default;
    virtual std::expected<void, BusStatus> read_reg(uint8_t reg, std::span<uint8_t> data) = 0;
    virtual std::expected<void, BusStatus> write_reg(uint8_t reg, std::span<const uint8_t> data) = 0;
};

/* Апаратні функції платформи */
extern void hal_gpio_write(uint32_t pin, bool level);
extern std::expected<void, BusStatus> hal_spi_sync_xfer(void* inst, std::span<const uint8_t> tx, std::span<uint8_t> rx);
extern std::expected<void, BusStatus> hal_i2c_sync_read(void* inst, uint8_t addr, uint8_t reg, std::span<uint8_t> data);
extern std::expected<void, BusStatus> hal_i2c_sync_write(void* inst, uint8_t addr, uint8_t reg, std::span<const uint8_t> data);

/* RAII-керування лінією Chip Select для SPI */
class ChipSelectGuard {
public:
    explicit ChipSelectGuard(uint32_t cs_pin) noexcept : cs_pin_(cs_pin) {
        hal_gpio_write(cs_pin_, false); /* Активуємо CS */
    }
    ~ChipSelectGuard() noexcept {
        hal_gpio_write(cs_pin_, true);  /* Деактивуємо CS */
    }
    ChipSelectGuard(const ChipSelectGuard&) = delete;
    ChipSelectGuard& operator=(const ChipSelectGuard&) = delete;

private:
    uint32_t cs_pin_;
};

/* SPI-адаптер */
class SpiBusDevice final : public IBusDevice {
public:
    constexpr SpiBusDevice(void* spi_inst, uint32_t cs_pin) noexcept
        : spi_inst_(spi_inst), cs_pin_(cs_pin) {
        hal_gpio_write(cs_pin_, true);
    }

    std::expected<void, BusStatus> read_reg(uint8_t reg, std::span<uint8_t> data) override {
        ChipSelectGuard cs(cs_pin_);
        uint8_t cmd = reg | 0x80U;
        auto res = hal_spi_sync_xfer(spi_inst_, std::span(&cmd, 1), {});
        if (!res) return res;
        if (!data.empty()) {
            return hal_spi_sync_xfer(spi_inst_, {}, data);
        }
        return {};
    }

    std::expected<void, BusStatus> write_reg(uint8_t reg, std::span<const uint8_t> data) override {
        ChipSelectGuard cs(cs_pin_);
        uint8_t cmd = reg & 0x7FU;
        auto res = hal_spi_sync_xfer(spi_inst_, std::span(&cmd, 1), {});
        if (!res) return res;
        if (!data.empty()) {
            return hal_spi_sync_xfer(spi_inst_, data, {});
        }
        return {};
    }

private:
    void* spi_inst_;
    uint32_t cs_pin_;
};

/* I2C-адаптер */
class I2cBusDevice final : public IBusDevice {
public:
    constexpr I2cBusDevice(void* i2c_inst, uint8_t addr_7bit) noexcept
        : i2c_inst_(i2c_inst), addr_7bit_(addr_7bit) {}

    std::expected<void, BusStatus> read_reg(uint8_t reg, std::span<uint8_t> data) override {
        return hal_i2c_sync_read(i2c_inst_, addr_7bit_, reg, data);
    }

    std::expected<void, BusStatus> write_reg(uint8_t reg, std::span<const uint8_t> data) override {
        return hal_i2c_sync_write(i2c_inst_, addr_7bit_, reg, data);
    }

private:
    void* i2c_inst_;
    uint8_t addr_7bit_;
};

/* Драйвер IMU (ICM-42688-P) */
struct ImuReading {
    float accel_x, accel_y, accel_z; /* у м/с² */
    float gyro_x,  gyro_y,  gyro_z;  /* у рад/с */
};

class Icm42688Driver {
public:
    explicit constexpr Icm42688Driver(IBusDevice& bus) noexcept : bus_(bus) {}

    std::expected<ImuReading, BusStatus> read() {
        std::array<uint8_t, 12> raw{};
        auto res = bus_.read_reg(0x1F, raw);
        if (!res) return std::unexpected(res.error());

        auto parse_i16 = [](uint8_t h, uint8_t l) -> int16_t {
            return static_cast<int16_t>((static_cast<uint16_t>(h) << 8) | l);
        };

        constexpr float ACCEL_SCALE = 9.80665f / 2048.0f;     /* ±16g */
        constexpr float GYRO_SCALE  = 0.0174532925f / 16.4f; /* ±2000 dps */

        return ImuReading{
            .accel_x = parse_i16(raw[0], raw[1]) * ACCEL_SCALE,
            .accel_y = parse_i16(raw[2], raw[3]) * ACCEL_SCALE,
            .accel_z = parse_i16(raw[4], raw[5]) * ACCEL_SCALE,
            .gyro_x  = parse_i16(raw[6], raw[7]) * GYRO_SCALE,
            .gyro_y  = parse_i16(raw[8], raw[9]) * GYRO_SCALE,
            .gyro_z  = parse_i16(raw[10], raw[11]) * GYRO_SCALE
        };
    }

private:
    IBusDevice& bus_;
};

/* Драйвер барометра (MS5611) */
class Ms5611Driver {
public:
    explicit constexpr Ms5611Driver(IBusDevice& bus) noexcept : bus_(bus) {}

    std::expected<uint32_t, BusStatus> read_adc_raw() {
        std::array<uint8_t, 3> buf{};
        auto res = bus_.read_reg(0x00, buf);
        if (!res) return std::unexpected(res.error());

        uint32_t val = (static_cast<uint32_t>(buf[0]) << 16) |
                       (static_cast<uint32_t>(buf[1]) << 8)  |
                       buf[2];
        return val;
    }

private:
    IBusDevice& bus_;
};

} // namespace avionics
