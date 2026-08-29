#include "sensor_rail.hpp"

#include <array>
#include <span>

#include "bus_quiesce.hpp"

namespace lowpower {
namespace {

using namespace std::chrono_literals;

// Плата: барометр BME280 і акселерометр LIS2DH12 на спільній шині 3V3_SENS,
// яку вмикає P-MOSFET. Підтяжки I2C сидять на ТІЙ САМІЙ шині, тому зникають
// разом із живленням — фантомити датчики мікроконтролеру нема чим.
constexpr std::uint8_t kBme280Addr = 0x76;
constexpr std::uint8_t kBme280RegId = 0xD0;
constexpr std::uint8_t kBme280IdValue = 0x60;
constexpr std::uint8_t kBme280RegCtrl = 0xF4;
constexpr std::uint8_t kBme280Sleep = 0x00;   // режим 00 — сон
constexpr std::uint8_t kBme280Forced = 0x25;  // передискретизація ×1, один вимір
constexpr std::uint8_t kBme280RegTemp = 0xFA;

constexpr std::uint8_t kLis2dhAddr = 0x19;
constexpr std::uint8_t kLis2dhRegCtrl1 = 0x20;
constexpr std::uint8_t kLis2dhPowerDown = 0x00;
constexpr std::uint8_t kLis2dhOdr100Hz = 0x57;

struct RegisterWrite {
    std::uint8_t addr7;
    std::uint8_t reg;
    std::uint8_t value;
};

// Команди «засни» обом датчикам. Це не ввічливість: акселерометр із
// увімкненим перетворювачем тягне сотні мікроампер навіть тоді, коли його
// вже ніхто не читає, а барометр посеред виміру не відпустить шину.
constexpr std::array kStandbyCommands{
    RegisterWrite{kBme280Addr, kBme280RegCtrl, kBme280Sleep},
    RegisterWrite{kLis2dhAddr, kLis2dhRegCtrl1, kLis2dhPowerDown},
};

constexpr std::array kWakeCommands{
    RegisterWrite{kLis2dhAddr, kLis2dhRegCtrl1, kLis2dhOdr100Hz},
    RegisterWrite{kBme280Addr, kBme280RegCtrl, kBme280Forced},
};

constexpr auto kStepTimeout = 2000us;   // із запасом на розтягування такту
constexpr auto kQuiesceTimeout = 5000us;

// Стікач 10 кОм і 4.7 мкФ блокувальної ємності дають tau ≈ 47 мс; п'яти
// постійних часу досить, щоб напруга впала нижче порога захисних діодів.
constexpr auto kDischargeTime = 235ms;
// Наростання шини плюс час старту BME280 після подання живлення.
constexpr auto kStartupTime = 5ms;

} // namespace

Status SensorRail::wait_isr(mcu::u32 flag)
{
    auto& i2c = mcu::i2c1();
    for (auto left = kStepTimeout.count();; --left) {
        const auto isr = i2c.isr;
        // NACK — не таймаут, а відповідь заліза: за цією адресою нікого немає.
        if ((isr & mcu::bits::kI2cIsrNackf) != 0U) {
            i2c.icr = mcu::bits::kI2cIcrNackcf | mcu::bits::kI2cIcrStopcf;
            return std::unexpected{Error::SensorNack};
        }
        if ((isr & flag) != 0U) { return {}; }
        if (left <= 0) { return std::unexpected{Error::SensorTimeout}; }
        mcu::delay(1us);
    }
}

Status SensorRail::finish_transfer()
{
    auto result = wait_isr(mcu::bits::kI2cIsrStopf);
    mcu::i2c1().icr = mcu::bits::kI2cIcrStopcf;
    mcu::i2c1().cr2 = 0U;
    return result;
}

Status SensorRail::write_reg(std::uint8_t addr7, std::uint8_t reg, std::uint8_t value)
{
    auto& i2c = mcu::i2c1();
    if ((i2c.cr1 & mcu::bits::kI2cPe) == 0U) {
        mcu::set_bits(i2c.cr1, mcu::bits::kI2cPe);  // після сну модуль лишається вимкненим
    }

    i2c.cr2 = mcu::i2c_addr(addr7) | mcu::i2c_nbytes(2) |
              mcu::bits::kI2cAutoEnd | mcu::bits::kI2cStart;

    for (const std::uint8_t byte : {reg, value}) {
        if (auto st = wait_isr(mcu::bits::kI2cIsrTxis); !st) { return st; }
        i2c.txdr = byte;
    }

    return finish_transfer();
}

Status SensorRail::read_regs(std::uint8_t addr7, std::uint8_t reg,
                             std::span<std::uint8_t> dst)
{
    auto& i2c = mcu::i2c1();
    if ((i2c.cr1 & mcu::bits::kI2cPe) == 0U) {
        mcu::set_bits(i2c.cr1, mcu::bits::kI2cPe);
    }

    // Фаза 1: номер регістра БЕЗ AUTOEND, щоб утримати шину до повторного старту.
    i2c.cr2 = mcu::i2c_addr(addr7) | mcu::i2c_nbytes(1) | mcu::bits::kI2cStart;
    if (auto st = wait_isr(mcu::bits::kI2cIsrTxis); !st) { return st; }
    i2c.txdr = reg;
    if (auto st = wait_isr(mcu::bits::kI2cIsrTc); !st) { return st; }

    // Фаза 2: повторний старт на читання, автоматичний STOP наприкінці.
    i2c.cr2 = mcu::i2c_addr(addr7) | mcu::i2c_nbytes(dst.size()) |
              mcu::bits::kI2cRdWrn | mcu::bits::kI2cAutoEnd | mcu::bits::kI2cStart;

    for (auto& byte : dst) {
        if (auto st = wait_isr(mcu::bits::kI2cIsrRxne); !st) { return st; }
        byte = static_cast<std::uint8_t>(i2c.rxdr);
    }

    return finish_transfer();
}

Status SensorRail::shutdown()
{
    for (const auto& cmd : kStandbyCommands) {
        if (auto st = write_reg(cmd.addr7, cmd.reg, cmd.value); !st) { return st; }
    }

    if (auto st = quiesce_all(kQuiesceTimeout); !st) { return st; }

    // Одиниця на затворі P-MOSFET закриває ключ.
    gate_.write(true);
    powered_ = false;

    // Витримка на розряд. Поки на блокувальних ємностях датчика лишається
    // напруга, будь-який вивід мікроконтролера, зведений у нуль, стає для неї
    // стоком через нижній захисний діод.
    mcu::delay(kDischargeTime);
    return {};
}

Status SensorRail::power_up()
{
    gate_.write(false);
    mcu::delay(kStartupTime);
    powered_ = true;

    // Виводи й модуль I2C повертаються до роботи.
    mcu::Pin{mcu::gpiob(), 8}.alternate(4);
    mcu::Pin{mcu::gpiob(), 9}.alternate(4);
    mcu::set_bits(mcu::i2c1().cr1, mcu::bits::kI2cPe);

    // Перевірка ідентифікатора: якщо шина не піднялася або підтяжки зникли
    // разом із живленням, читання дасть 0x00 чи 0xFF — краще дізнатися про це
    // тут, ніж прийняти сміття за вимір.
    std::uint8_t id{};
    if (auto st = read_regs(kBme280Addr, kBme280RegId, {&id, 1}); !st) { return st; }
    if (id != kBme280IdValue) { return std::unexpected{Error::SensorWrongId}; }

    for (const auto& cmd : kWakeCommands) {
        if (auto st = write_reg(cmd.addr7, cmd.reg, cmd.value); !st) { return st; }
    }
    return {};
}

std::expected<std::int32_t, Error> SensorRail::read_temperature_raw()
{
    // Один вимір на вимогу; ×1 передискретизації — близько 7 мс.
    if (auto st = write_reg(kBme280Addr, kBme280RegCtrl, kBme280Forced); !st) {
        return std::unexpected{st.error()};
    }
    mcu::delay(10ms);

    std::array<std::uint8_t, 3> raw{};
    if (auto st = read_regs(kBme280Addr, kBme280RegTemp, raw); !st) {
        return std::unexpected{st.error()};
    }

    // Двадцять значущих бітів: старший, середній і чотири біти молодшого.
    return static_cast<std::int32_t>((static_cast<mcu::u32>(raw[0]) << 12) |
                                     (static_cast<mcu::u32>(raw[1]) << 4) |
                                     (static_cast<mcu::u32>(raw[2]) >> 4));
}

} // namespace lowpower
