#pragma once

#include <array>
#include <cstdint>

#include "fct.hpp"
#include "hal.hpp"

// Шини до периферії. Тестер ніколи не довіряє тому, що шина вільна:
// спершу примусово вивільняє I2C, і аж тоді звіряє ідентифікатори.

namespace fct {

inline constexpr std::uint32_t kI2cTimeoutUs = 5'000;
inline constexpr std::uint32_t kSpiTimeoutUs = 8'000;
inline constexpr std::uint32_t kI2cHalfBitUs = 5;  // ~100 кГц у bit-banging

// RAII: конструктор вивільняє шину й повертає піни периферії, деструктор
// гасить її навіть тоді, коли тест вийшов посеред перевірки.
class I2cBus {
public:
    I2cBus() noexcept : released_{recover()} {}

    ~I2cBus()
    {
        hal::i2c_pins_to_peripheral();
    }

    I2cBus(const I2cBus&) = delete;
    I2cBus& operator=(const I2cBus&) = delete;

    [[nodiscard]] bool released() const noexcept { return released_; }

    [[nodiscard]] std::expected<std::uint8_t, Failure> read_reg(
        std::uint8_t addr7, std::uint8_t reg) const noexcept
    {
        const auto value = hal::i2c_read_reg(addr7, reg, kI2cTimeoutUs);
        if (!value) {
            return fail(Error::Timeout, "Ведений не квитує адресу (NACK)",
                        addr7, "addr");
        }
        return *value;
    }

private:
    // Дев'ять тактів SCL вивільняють веденого, що завис посеред видачі байта
    // й тримає SDA притиснутою до землі. Робиться до ініціалізації периферії:
    // контролер у стані Bus Busy не дасть навіть почати транзакцію.
    static bool recover() noexcept
    {
        hal::i2c_pins_to_gpio();
        hal::i2c_sda_write(true);
        hal::i2c_scl_write(true);
        hal::delay_us(kI2cHalfBitUs);

        bool free_line = hal::i2c_sda_read();
        for (int pulse = 0; pulse < 9 && !free_line; ++pulse) {
            hal::i2c_scl_write(false);
            hal::delay_us(kI2cHalfBitUs);
            hal::i2c_scl_write(true);
            hal::delay_us(kI2cHalfBitUs);
            free_line = hal::i2c_sda_read();
        }

        // Стоп-умова: SDA 0→1 при високому SCL повертає веденого в idle.
        hal::i2c_scl_write(false);
        hal::i2c_sda_write(false);
        hal::delay_us(kI2cHalfBitUs);
        hal::i2c_scl_write(true);
        hal::delay_us(kI2cHalfBitUs);
        hal::i2c_sda_write(true);
        hal::delay_us(kI2cHalfBitUs);

        free_line = hal::i2c_sda_read();
        hal::i2c_pins_to_peripheral();
        hal::i2c_reinit();
        return free_line;
    }

    bool released_;
};

struct I2cDevice {
    std::string_view name;
    std::uint8_t addr7;
    std::uint8_t id_reg;
    std::uint8_t id_expected;
};

inline constexpr std::array<I2cDevice, 2> kI2cDevices{{
    {"ICM-42688 IMU", 0x68, 0x75, 0x47},  // WHO_AM_I
    {"BMP390 baro", 0x77, 0x00, 0x60}     // CHIP_ID
}};

inline Outcome test_i2c_devices() noexcept
{
    const I2cBus bus;
    if (!bus.released()) {
        // Дев'ять тактів не допомогли: SDA замкнена доріжкою або мертвим
        // чипом, а не завислою транзакцією.
        return fail(Error::BusLocked, "SDA лишилася низькою після 9 тактів SCL");
    }

    for (const auto& dev : kI2cDevices) {
        const auto id = bus.read_reg(dev.addr7, dev.id_reg);
        if (!id) {
            return std::unexpected(id.error());
        }
        if (*id != dev.id_expected) {
            return fail(Error::InvalidId, "Чужий або нечитний ідентифікатор",
                        *id, "id");
        }
        hal::watchdog_kick();
    }

    return pass("Усі ведені відгукнулися своїм ID",
                static_cast<std::int32_t>(kI2cDevices.size()), "devices");
}

struct JedecId {
    std::uint8_t manufacturer;
    std::uint8_t memory_type;
    std::uint8_t capacity;
};

// RAII на вибір кристала: CS відпускається й тоді, коли обмін не вдався.
class SpiSelect {
public:
    SpiSelect() noexcept { hal::spi_cs(true); }
    ~SpiSelect() { hal::spi_cs(false); }

    SpiSelect(const SpiSelect&) = delete;
    SpiSelect& operator=(const SpiSelect&) = delete;
};

[[nodiscard]] inline std::expected<JedecId, Failure> read_jedec_id() noexcept
{
    constexpr std::array<std::uint8_t, 4> tx{0x9F, 0x00, 0x00, 0x00};
    std::array<std::uint8_t, 4> rx{};

    {
        const SpiSelect cs;
        if (!hal::spi_xfer(tx, rx, kSpiTimeoutUs)) {
            return fail(Error::Timeout, "SPI: обмін не завершився");
        }
    }

    // Суцільні 0x00 чи 0xFF — це не ідентифікатор, а обірваний MISO.
    const bool stuck_low = rx[1] == 0x00 && rx[2] == 0x00 && rx[3] == 0x00;
    const bool stuck_high = rx[1] == 0xFF && rx[2] == 0xFF && rx[3] == 0xFF;
    if (stuck_low || stuck_high) {
        return fail(Error::BusLocked, "MISO застряг у 0/1: пайка або CS");
    }

    return JedecId{rx[1], rx[2], rx[3]};
}

inline Outcome test_spi_flash() noexcept
{
    const auto id = read_jedec_id();
    if (!id) {
        return std::unexpected(id.error());
    }
    // Очікуємо Winbond W25Q128: EF 40 18.
    if (id->manufacturer != 0xEF || id->memory_type != 0x40 || id->capacity != 0x18) {
        const std::int32_t packed = (std::int32_t{id->manufacturer} << 16) |
                                    (std::int32_t{id->memory_type} << 8) |
                                    std::int32_t{id->capacity};
        return fail(Error::InvalidId, "Незнайомий JEDEC ID або інший об'єм",
                    packed, "jedec");
    }

    // 0x18 → 2^24 байт = 16 МіБ.
    return pass("W25Q128 відповів своїм JEDEC ID",
                std::int32_t{1} << (id->capacity - 20), "MiB");
}

}  // namespace fct
