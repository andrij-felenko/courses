#include "board.hpp"

namespace board {
namespace {

using soc::PinMode;
using soc::PinPull;

constexpr std::array<const soc::GpioPort*, 3> kPorts{&soc::portA, &soc::portB, &soc::portC};

void shortSettle() noexcept
{
    for (volatile unsigned k = 0; k < 40U; ++k) {
    }
}

} // namespace

// Такт після Stop2 — MSI 4 МГц. Точність тут не потрібна, потрібна
// гарантовано не менша пауза.
void delayFor(std::chrono::milliseconds duration) noexcept
{
    for (std::int64_t ms = 0; ms < duration.count(); ++ms) {
        for (volatile unsigned k = 0; k < 400U; ++k) {
        }
    }
}

void initClocks() noexcept
{
    soc::rcc::ahb2enr.setBits(soc::rcc::gpioAEnable | soc::rcc::gpioBEnable
                              | soc::rcc::gpioCEnable);
    soc::rcc::apb1enr1.setBits(soc::rcc::pwrEnable);
    static_cast<void>(soc::rcc::apb1enr1.load()); // синхронізація шини
}

void initPins() noexcept
{
    // Ключ розмикаємо першим: після скидання затвор не заданий, і датчик
    // не має живитися, поки прошивка цього не вирішила.
    soc::portB.write(kRailGatePin, true);
    soc::portB.setPull(kRailGatePin, PinPull::None);
    soc::portB.setMode(kRailGatePin, PinMode::Output);

    allPinsToAnalog();

    soc::portC.write(kLedPin, false);
    soc::portC.setMode(kLedPin, PinMode::Output);

    // Кнопку зміщує зовнішній резистор 470 кОм; внутрішня підтяжка 40 кОм
    // додала б сюди ще 80 мкА.
    soc::portA.setPull(0U, PinPull::None);
    soc::portA.setMode(0U, PinMode::Input);
}

void led(bool on) noexcept
{
    soc::portC.setMode(kLedPin, PinMode::Output);
    soc::portC.write(kLedPin, on);
}

void railOn() noexcept
{
    soc::portB.write(kRailGatePin, false);
    delayFor(std::chrono::milliseconds{3}); // заряд блокувальних ємностей
}

void railOff() noexcept
{
    soc::portB.write(kRailGatePin, true);
    delayFor(std::chrono::milliseconds{2}); // розряд через власне навантаження
}

bool railIsDischarged() noexcept
{
    // Вхід вмикаємо на мить: тримати його цифровим постійно — влаштувати
    // собі рівно той наскрізний струм, який ми ловимо.
    soc::portB.setPull(kSensePin, PinPull::None);
    soc::portB.setMode(kSensePin, PinMode::Input);
    shortSettle();
    const bool stillPowered = soc::portB.read(kSensePin);
    soc::portB.setMode(kSensePin, PinMode::Analog);
    return !stillPowered;
}

void parkSwitchedDomain() noexcept
{
    // Порядок критичний: лінії до знеструмлюваного вузла притискаємо в нуль,
    // ПОКИ його шина ще під напругою. Інакше вихідний драйвер почне живити
    // датчик через верхній ESD-діод.
    for (const PinSpec& spec : kPlan) {
        if (spec.role != SleepRole::ParkLow) {
            continue;
        }
        spec.port->write(spec.number, false);
        spec.port->setPull(spec.number, PinPull::None);
        spec.port->setMode(spec.number, PinMode::Output);
    }
}

void allPinsToAnalog() noexcept
{
    for (const soc::GpioPort* port : kPorts) {
        for (std::uint8_t pin = 0; pin < 16U; ++pin) {
            switch (roleOf(*port, pin)) {
            case SleepRole::KeepHigh:
                port->setMode(pin, PinMode::Output);
                port->setPull(pin, PinPull::None);
                break;
            case SleepRole::Wakeup:
                break; // рівень задає зовнішній резистор
            case SleepRole::Analog:
            case SleepRole::ParkLow:
            case SleepRole::Sense:
                port->setMode(pin, PinMode::Analog);
                port->setPull(pin, PinPull::None);
                break;
            }
        }
        port->openAnalogSwitches();
    }
}

void applyStandbyPulls() noexcept
{
    // У Standby конфігурація GPIO втрачається, рівні задає блок живлення.
    // Затвор ключа мусить лишитися високим, інакше шина датчика оживе
    // разом зі сном.
    soc::pwr::pucrA.store(0U);
    soc::pwr::pdcrA.store(0U);
    soc::pwr::pucrB.store(soc::bit(kRailGatePin));
    soc::pwr::pdcrB.store(0U);
    soc::pwr::pucrC.store(0U);
    soc::pwr::pdcrC.store(0U);
    soc::pwr::cr3.setBits(soc::pwr::applyPullConfig);
}

FloatingPins auditFloating() noexcept
{
    FloatingPins report{};
    soc::Word* slots[]{&report.inPortA, &report.inPortB, &report.inPortC};

    for (std::size_t index = 0; index < kPorts.size(); ++index) {
        const soc::GpioPort& port = *kPorts[index];
        for (std::uint8_t pin = 0; pin < 16U; ++pin) {
            if (port.mode(pin) != PinMode::Input || port.pull(pin) != PinPull::None) {
                continue;
            }
            if (roleOf(port, pin) == SleepRole::Wakeup) {
                continue; // зміщений зовні — не плаває
            }
            *slots[index] |= soc::bit(pin);
            ++report.count;
        }
    }
    return report;
}

} // namespace board
