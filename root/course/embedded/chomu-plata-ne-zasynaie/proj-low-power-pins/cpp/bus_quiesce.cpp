#include "bus_quiesce.hpp"

namespace lowpower {
namespace {

using namespace std::chrono_literals;

// I2C1 на цій платі: PB8 — SCL, PB9 — SDA, альтернативна функція 4.
const mcu::Pin kScl{mcu::gpiob(), 8};
const mcu::Pin kSda{mcu::gpiob(), 9};
constexpr mcu::u32 kI2cAf = 4U;

// 100 кГц — це 10 мкс на період, отже 5 мкс на півперіод.
constexpr auto kHalfBit = 5us;

// Опитування прапорця з грубим таймаутом.
[[nodiscard]] bool wait_flag(volatile mcu::u32& reg, mcu::u32 mask, bool want_set,
                             std::chrono::microseconds timeout)
{
    for (auto left = timeout.count();; --left) {
        if (((reg & mask) != 0U) == want_set) { return true; }
        if (left <= 0) { return false; }
        mcu::delay(1us);
    }
}

void scl_pulse()
{
    kScl.write(true);
    mcu::delay(kHalfBit);
    kScl.write(false);
    mcu::delay(kHalfBit);
}

} // namespace

Status quiesce(mcu::UsartBlock& u, std::chrono::microseconds timeout)
{
    if ((u.cr1 & mcu::bits::kUsartUe) == 0U) { return {}; }

    // TXE каже лише те, що байт переїхав з буфера у зсувний регістр. Зупинити
    // тактування тут означає віддати приймачеві обірваний кадр і Framing Error.
    // Чекаємо TC — момент, коли стоповий біт уже на лінії.
    if ((u.cr1 & mcu::bits::kUsartTe) != 0U) {
        if (!wait_flag(u.isr, mcu::bits::kUsartIsrTc, true, timeout)) {
            return std::unexpected{Error::UartNotDrained};
        }
    }

    mcu::clear_bits(u.cr1, mcu::bits::kUsartUe);
    return {};
}

Status quiesce(mcu::SpiBlock& s, std::chrono::microseconds timeout)
{
    if ((s.cr1 & mcu::bits::kSpiSpe) == 0U) { return {}; }

    // Спершу має спорожніти черга передачі, і лише потім знімається BSY.
    if (!wait_flag(s.sr, mcu::bits::kSpiSrFtlvl, false, timeout) ||
        !wait_flag(s.sr, mcu::bits::kSpiSrBsy, false, timeout)) {
        return std::unexpected{Error::SpiBusy};
    }

    mcu::clear_bits(s.cr1, mcu::bits::kSpiSpe);
    return {};
}

Status quiesce(mcu::I2cBlock& i, std::chrono::microseconds timeout)
{
    if ((i.cr1 & mcu::bits::kI2cPe) == 0U) { return {}; }

    if (!wait_flag(i.isr, mcu::bits::kI2cIsrBusy, false, timeout)) {
        // Шина зависла: ведений тримає лінію. Знімаємо PE й пробуємо
        // розклинити — інакше після пробудження модуль не видасть START.
        mcu::clear_bits(i.cr1, mcu::bits::kI2cPe);
        if (auto rec = recover_i2c_bus(); !rec) { return rec; }
        return std::unexpected{Error::I2cBusy};
    }

    // Зняття PE відпускає обидві лінії у високий імпеданс — саме те, що треба
    // перед знеструмленням веденого.
    mcu::clear_bits(i.cr1, mcu::bits::kI2cPe);
    return {};
}

Status quiesce_all(std::chrono::microseconds timeout)
{
    return quiesce(mcu::usart2(), timeout)
        .and_then([&] { return quiesce(mcu::spi1(), timeout); })
        .and_then([&] { return quiesce(mcu::i2c1(), timeout); });
}

Status recover_i2c_bus()
{
    // Обидві лінії стають виходами з відкритим стоком: одиниця на такому
    // виході — це відпущена лінія, а не 3.3 В у ведений.
    for (const auto& pin : {kScl, kSda}) {
        pin.open_drain(true);
        pin.write(true);
        pin.mode(mcu::Mode::Output);
    }
    mcu::delay(kHalfBit);

    // Дев'ять тактів: ведений добиває недоказаний байт і відпускає SDA.
    for (unsigned n = 0; n < 9 && !kSda.read(); ++n) {
        scl_pulse();
    }
    const bool freed = kSda.read();

    // Умова STOP: SDA вниз, SCL вгору, SDA вгору. Без неї ведений лишиться
    // вважати, що транзакція триває.
    kSda.write(false);
    mcu::delay(kHalfBit);
    kScl.write(true);
    mcu::delay(kHalfBit);
    kSda.write(true);
    mcu::delay(kHalfBit);

    kScl.alternate(kI2cAf);
    kSda.alternate(kI2cAf);

    if (!freed) { return std::unexpected{Error::I2cStuck}; }
    return {};
}

} // namespace lowpower
