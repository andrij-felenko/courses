// Сон як область видимості.
//
// Ізоляція виводів має рівно одну небезпечну властивість: якщо десь між
// підготовкою і пробудженням з'явиться ранній вихід, плата лишиться з усіма
// ніжками в аналоговому режимі й без UART, тобто німою. Сторож знімає це
// питання з порядку денного — відновлення прив'язане до виходу з блоку, а не
// до дисципліни того, хто писав гілки.
#pragma once

#include <chrono>

#include "mcu.hpp"
#include "pin_isolation.hpp"
#include "sensor_rail.hpp"
#include "status.hpp"
#include "wakeup.hpp"

namespace lowpower {

class SleepScope {
public:
    // Конструктор виконує кроки 1–5 і 7: standby датчикам, зупинка шин,
    // розмикання ключа, витримка на розряд, виводи в аналог, DBGMCU у нуль.
    SleepScope(SensorRail& rail, PinIsolator& pins) noexcept
        : pins_{pins}, prepared_{rail.shutdown()}
    {
        // Навіть якщо датчик не відповів, спати треба: виріб на батарейці не
        // може не заснути через одну німу мікросхему. Відмова не губиться —
        // вона лежить у prepared() і потрапить у журнал після пробудження.
        pins_.isolate();
    }

    ~SleepScope() noexcept { pins_.restore(); }

    SleepScope(const SleepScope&) = delete;
    SleepScope& operator=(const SleepScope&) = delete;

    [[nodiscard]] const Status& prepared() const noexcept { return prepared_; }

private:
    PinIsolator& pins_;
    Status prepared_;
};

// Власне зупинка ядра. Виділено окремо, бо порядок цих п'яти рядків і є
// відповідь на питання «чому плата не засинає».
inline void stop_until_interrupt() noexcept
{
    // Режим Stop 2: ядро й більшість тактування зупинені, пам'ять ціла.
    mcu::pwr().cr1 = (mcu::pwr().cr1 & ~mcu::bits::kPwrLpmsMask) |
                     mcu::bits::kPwrLpmsStop2;
    mcu::pwr().scr = mcu::bits::kPwrScrCwuf;
    mcu::set_bits(mcu::scb_scr(), mcu::bits::kScrSleepDeep);

    {
        // Заборона переривань довкола WFI — не для швидкодії. Між очищенням
        // черги й самим WFI не має бути щілини, у якій ядро дістане прапорець
        // і прокинеться до того, як тактове дерево зупинилося. Замаскований
        // WFI усе одно прокидається, а обробник відпрацює на виході з блоку.
        mcu::IrqLock lock;
        wakeup::clear_pending();
        mcu::dsb();
        mcu::wfi();
        mcu::isb();
    }

    mcu::clear_bits(mcu::scb_scr(), mcu::bits::kScrSleepDeep);
}

// Повний цикл сну. Повертає те, що не вдалося підготувати, — або порожній успіх.
[[nodiscard]] inline Status deep_sleep_for(SensorRail& rail, PinIsolator& pins,
                                           std::chrono::seconds duration)
{
    // Джерело пробудження заводиться ДО ізоляції виводів і до заборони
    // переривань: плата, що заснула без будильника, чекатиме тільки кнопки.
    wakeup::arm(duration);

    SleepScope scope{rail, pins};
    stop_until_interrupt();
    return scope.prepared();
}

} // namespace lowpower
