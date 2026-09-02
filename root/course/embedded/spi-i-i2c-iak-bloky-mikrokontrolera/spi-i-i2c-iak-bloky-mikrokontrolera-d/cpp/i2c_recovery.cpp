#include "i2c_recovery.hpp"

#include "peripherals.hpp"

namespace drv {
namespace {

constexpr unsigned sclPin = 6u;
constexpr unsigned sdaPin = 7u;
constexpr unsigned i2c1AltFunction = 4u;
constexpr std::uint32_t halfPeriodUs = 5u;  // половина періоду 100 кГц, із запасом

// Хоч би як вийшли з процедури, ніжки мають повернутися блоку I2C,
// а сам блок — отримати програмний скид.
struct PeripheralRestorer {
    ~PeripheralRestorer()
    {
        mcu::configurePin(mcu::gpioB(), sclPin, mcu::PinMode::Alternate, true, i2c1AltFunction);
        mcu::configurePin(mcu::gpioB(), sdaPin, mcu::PinMode::Alternate, true, i2c1AltFunction);
        // SWRST не лікує зовнішній чіп, зате знімає засувку BUSY, яку блок
        // защіпнув, побачивши SDA=0 при високій SCL.
        mcu::i2c1().cr1 = mcu::i2c_cr1::swrst;
        mcu::delayUs(2u);
        mcu::i2c1().cr1 = 0u;
    }
};

void formStopCondition() noexcept
{
    // Ручний STOP: перепад SDA з 0 в 1 при високій SCL повертає автомати
    // всіх ведених на шині у стан спокою.
    auto& port = mcu::gpioB();
    mcu::configurePin(port, sdaPin, mcu::PinMode::Output, true);
    mcu::writePin(port, sclPin, false);
    mcu::writePin(port, sdaPin, false);
    mcu::delayUs(halfPeriodUs);
    mcu::writePin(port, sclPin, true);
    mcu::delayUs(halfPeriodUs);
    mcu::writePin(port, sdaPin, true);
    mcu::delayUs(halfPeriodUs);
}

}  // namespace

std::expected<BusState, RecoveryError> recoverI2c1Bus() noexcept
{
    mcu::rcc().ahb1enr |= mcu::rcc_bits::gpiobEn;
    mcu::rcc().apb1enr |= mcu::rcc_bits::i2c1En;

    // Поки PE=1, ніжки належать периферії — блок треба вимкнути
    mcu::i2c1().cr1 &= ~mcu::i2c_cr1::pe;

    PeripheralRestorer restorer;
    auto& port = mcu::gpioB();

    mcu::configurePin(port, sclPin, mcu::PinMode::Output, true);
    mcu::configurePin(port, sdaPin, mcu::PinMode::Input, true);
    mcu::writePin(port, sclPin, true);
    mcu::delayUs(halfPeriodUs * 2u);

    if (mcu::readPin(port, sdaPin)) {
        formStopCondition();
        return BusState::AlreadyFree;
    }

    // Ведений завис усередині свого байта: досилаємо такти, поки він не
    // викладе решту бітів і не відпустить SDA перед тактом ACK.
    // Дев'ять — байт плюс такт підтвердження.
    for (int i = 0; i < 9; ++i) {
        mcu::writePin(port, sclPin, false);
        mcu::delayUs(halfPeriodUs);
        mcu::writePin(port, sclPin, true);
        mcu::delayUs(halfPeriodUs);

        if (mcu::readPin(port, sdaPin)) {
            formStopCondition();
            return BusState::Released;
        }
    }

    return std::unexpected(RecoveryError::StuckLow);
}

}  // namespace drv
