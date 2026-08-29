#include "thermometer.hpp"

#include <array>
#include <chrono>

#include "board.hpp"

namespace sensor {
namespace {

using soc::PinMode;
using soc::PinPull;

constexpr std::uint8_t kSclPin = 6U;
constexpr std::uint8_t kSdaPin = 7U;
constexpr soc::Word kAlternateI2c1 = 4U;
constexpr std::uint32_t kSpinLimit = 20'000U;

void pinsToAlternate() noexcept
{
    soc::portB.setOpenDrain(kSclPin, true);
    soc::portB.setOpenDrain(kSdaPin, true);
    soc::portB.selectAlternate(kSclPin, kAlternateI2c1);
    soc::portB.selectAlternate(kSdaPin, kAlternateI2c1);
    // Підтяжки зовнішні й живляться з комутованої шини: внутрішні тут
    // були б витоком у бік знеструмленого датчика.
    soc::portB.setPull(kSclPin, PinPull::None);
    soc::portB.setPull(kSdaPin, PinPull::None);
    soc::portB.setMode(kSclPin, PinMode::Alternate);
    soc::portB.setMode(kSdaPin, PinMode::Alternate);
}

[[nodiscard]] std::expected<void, BusError> waitFor(soc::Word flags) noexcept
{
    BusError failure = BusError::Timeout;

    const bool settled = hal::spinUntil(
        [&]() noexcept {
            const soc::Word status = soc::i2c1::status.load();
            if ((status & (soc::i2c1::busError | soc::i2c1::arbitrationLost)) != 0U) {
                failure = BusError::Arbitration;
                return true;
            }
            if ((status & soc::i2c1::nackReceived) != 0U) {
                failure = BusError::Nack;
                return true;
            }
            if ((status & flags) != 0U) {
                failure = BusError::Timeout;
                return true;
            }
            return false;
        },
        kSpinLimit);

    if (!settled) {
        return std::unexpected{BusError::Timeout};
    }
    if ((soc::i2c1::status.load() & flags) != 0U) {
        return {};
    }
    soc::i2c1::clearFlags.store(soc::i2c1::clearAll);
    return std::unexpected{failure};
}

[[nodiscard]] std::expected<void, BusError> beginTransfer(std::uint8_t address7,
                                                          std::uint8_t bytes,
                                                          bool reading,
                                                          bool autoEnd) noexcept
{
    if (soc::i2c1::status.anyOf(soc::i2c1::busy)) {
        return std::unexpected{BusError::Busy};
    }

    soc::Word control = (static_cast<soc::Word>(address7) << 1U)
                      | (static_cast<soc::Word>(bytes) << soc::i2c1::byteCountShift)
                      | soc::i2c1::start;
    if (reading) {
        control |= soc::i2c1::readTransfer;
    }
    if (autoEnd) {
        control |= soc::i2c1::autoEnd;
    }
    soc::i2c1::control2.store(control);
    return {};
}

void forceStop() noexcept
{
    soc::i2c1::control2.setBits(soc::i2c1::stop);
    soc::i2c1::clearFlags.store(soc::i2c1::clearAll);
}

} // namespace

bool busStuck() noexcept
{
    // У спокої обидві лінії мусять бути вгорі — їх тягнуть зовнішні
    // резистори. Низький рівень означає, що хтось тримає шину.
    soc::portB.setMode(kSclPin, PinMode::Input);
    soc::portB.setMode(kSdaPin, PinMode::Input);
    board::delayFor(std::chrono::milliseconds{1});
    return !soc::portB.read(kSdaPin) || !soc::portB.read(kSclPin);
}

std::expected<void, BusError> recoverBus() noexcept
{
    // До дев'яти тактів SCL, поки раб не доотримає недописаний байт
    // і не відпустить SDA, потім умова STOP.
    soc::i2c1::control1.clearBits(soc::i2c1::peripheralEnable);

    soc::portB.setOpenDrain(kSclPin, true);
    soc::portB.setOpenDrain(kSdaPin, true);
    soc::portB.write(kSclPin, true);
    soc::portB.setMode(kSclPin, PinMode::Output);
    soc::portB.setMode(kSdaPin, PinMode::Input);

    for (unsigned pulse = 0; pulse < 9U && !soc::portB.read(kSdaPin); ++pulse) {
        soc::portB.write(kSclPin, false);
        board::delayFor(std::chrono::milliseconds{1});
        soc::portB.write(kSclPin, true);
        board::delayFor(std::chrono::milliseconds{1});
    }

    soc::portB.write(kSdaPin, false);
    soc::portB.setMode(kSdaPin, PinMode::Output);
    board::delayFor(std::chrono::milliseconds{1});
    soc::portB.write(kSclPin, true);
    board::delayFor(std::chrono::milliseconds{1});
    soc::portB.write(kSdaPin, true); // STOP: SDA вгору при високому SCL
    board::delayFor(std::chrono::milliseconds{1});
    soc::portB.setMode(kSdaPin, PinMode::Input);

    const bool freed = soc::portB.read(kSdaPin);
    pinsToAlternate();
    soc::i2c1::control1.setBits(soc::i2c1::peripheralEnable);

    if (!freed) {
        return std::unexpected{BusError::Stuck};
    }
    return {};
}

std::expected<BusSession, BusError> BusSession::open() noexcept
{
    soc::rcc::apb1enr1.setBits(soc::rcc::i2c1Enable);
    static_cast<void>(soc::rcc::apb1enr1.load());

    soc::i2c1::control1.clearBits(soc::i2c1::peripheralEnable);
    soc::i2c1::timing.store(soc::i2c1::timing100kHz);

    if (busStuck()) {
        if (const auto recovered = recoverBus(); !recovered) {
            soc::rcc::apb1enr1.clearBits(soc::rcc::i2c1Enable);
            return std::unexpected{recovered.error()};
        }
    }

    pinsToAlternate();
    soc::i2c1::clearFlags.store(soc::i2c1::clearAll);
    soc::i2c1::control1.setBits(soc::i2c1::peripheralEnable);
    return BusSession{};
}

BusSession::~BusSession() noexcept
{
    if (!live_) {
        return;
    }
    soc::i2c1::control1.clearBits(soc::i2c1::peripheralEnable);
    soc::rcc::apb1enr1.clearBits(soc::rcc::i2c1Enable);
    // Виводи паркує board::SensorRail: вони йдуть у знеструмлений домен,
    // і режим AF на них означав би живлення датчика через ESD-діод.
}

std::expected<void, BusError> BusSession::readRegister(std::uint8_t address7,
                                                       std::uint8_t reg,
                                                       std::span<std::uint8_t> out) const noexcept
{
    if (out.empty()) {
        return std::unexpected{BusError::Busy};
    }

    // Фаза 1: покажчик регістра, без STOP.
    if (const auto started = beginTransfer(address7, 1U, false, false); !started) {
        return started;
    }
    if (const auto ready = waitFor(soc::i2c1::txInterruptStatus); !ready) {
        forceStop();
        return ready;
    }
    soc::i2c1::transmit.store(reg);

    if (const auto done = waitFor(soc::i2c1::transferComplete); !done) {
        forceStop();
        return done;
    }

    // Фаза 2: повторний старт на читання з автоматичним STOP.
    if (const auto started = beginTransfer(address7, static_cast<std::uint8_t>(out.size()),
                                           true, true);
        !started) {
        return started;
    }
    for (std::uint8_t& byte : out) {
        if (const auto ready = waitFor(soc::i2c1::rxNotEmpty); !ready) {
            forceStop();
            return ready;
        }
        byte = static_cast<std::uint8_t>(soc::i2c1::receive.load());
    }

    const auto stopped = waitFor(soc::i2c1::stopDetected);
    soc::i2c1::clearFlags.store(soc::i2c1::clearAll);
    return stopped;
}

std::expected<Celsius, BusError> Thermometer::read(const BusSession& bus) const noexcept
{
    std::array<std::uint8_t, 2> raw{};

    return bus.readRegister(address_, 0x00U, raw).transform([&raw]() noexcept {
        const auto word = static_cast<std::int16_t>(
            (static_cast<std::uint16_t>(raw[0]) << 8U) | raw[1]);
        return Celsius{static_cast<std::int16_t>(word >> 7)}; // крок 0.5 °C
    });
}

} // namespace sensor
