// bus_guard.cpp — дев'ять тактів, умова STOP і облік невдач.

#include "field/bus_guard.hpp"

#include <chrono>

#include "field/platform.hpp"

namespace field {
namespace {

constexpr std::chrono::microseconds kHalfPeriod{5};  // ≈100 кГц ручного тактування
constexpr int kRecoverClocks = 9;  // вісім бітів байта плюс такт квитанції

}  // namespace

BusGuard::BusGuard(FaultLog& log, std::uint8_t address) : log_{log}, address_{address} {
    plat::i2cInit();
}

bool BusGuard::rescue() {
    bool released = false;

    {
        // Поки живий цей об'єкт, ніжки наші. Вийти звідси, не повернувши їх
        // периферії, неможливо навіть по помилковій гілці — за це відповідає
        // деструктор, а не наша пам'ять.
        plat::PinControl pins;

        pins.writeSda(true);
        pins.writeScl(true);
        plat::delayFor(kHalfPeriod * 2);

        released = pins.readSda();

        for (int i = 0; i < kRecoverClocks && !released; ++i) {
            // Кожен такт витягує з раба один зайвий біт. Рано чи пізно він
            // доходить до кінця байта, бачить заперечення й відпускає SDA.
            pins.writeScl(false);
            plat::delayFor(kHalfPeriod);
            pins.writeScl(true);
            plat::delayFor(kHalfPeriod);

            if (!pins.readScl()) {
                // SCL не піднявся навіть відпущений: це вже не завислий раб,
                // а замикання лінії або обірвана підтяжка. Тактувати марно.
                break;
            }
            released = pins.readSda();
        }

        if (released) {
            // Умова STOP: SDA з нуля в одиницю при високому SCL. Без неї раб
            // лишиться вважати, що транзакція триває, і зависне знову на
            // першому ж нашому START.
            pins.writeSda(false);
            plat::delayFor(kHalfPeriod);
            pins.writeScl(true);
            plat::delayFor(kHalfPeriod);
            pins.writeSda(true);
            plat::delayFor(kHalfPeriod * 2);
        }
    }

    ++recoveries_;
    log_.noteBusRecovery();
    return released;
}

BusHealth BusGuard::check() {
    const auto probe = plat::i2cProbe(address_);
    if (probe) {
        failStreak_ = 0;
        hopeless_ = 0;
        return BusHealth::Ok;
    }

    ++failStreak_;

    if (probe.error() == plat::HwError::Nack) {
        // Лінії живі, просто ніхто не озвався. Тактувати тут нічого: або
        // давач ще піднімається після власного скидання, або його вже немає —
        // обидва випадки лікуються не порятунком шини.
        return BusHealth::Silent;
    }

    // Busy чи Timeout — лінію тримають унизу.
    if (!rescue()) {
        ++hopeless_;
        return BusHealth::Dead;
    }

    if (plat::i2cProbe(address_)) {
        failStreak_ = 0;
        hopeless_ = 0;
        return BusHealth::Recovered;
    }

    // SDA відпустили, але раб усе одно мовчить: розчепірили лінію, не
    // полагодивши причину.
    ++hopeless_;
    return BusHealth::Stuck;
}

bool BusGuard::read(std::uint8_t reg, std::span<std::uint8_t> buf) {
    if (plat::i2cReadReg(address_, reg, buf)) {
        failStreak_ = 0;
        return true;
    }
    ++failStreak_;
    return false;
}

}  // namespace field
