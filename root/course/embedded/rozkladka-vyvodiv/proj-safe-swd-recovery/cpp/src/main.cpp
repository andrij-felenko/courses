#include "mcu/boot_guard.hpp"
#include "mcu/pin.hpp"
#include "mcu/system_clock.hpp"

using namespace std::chrono_literals;

namespace {

constexpr mcu::PinConfig kOutput{mcu::Mode::Output, mcu::Pull::None, mcu::Speed::Low,
                                 mcu::OutputType::PushPull, 0};

constexpr std::uint8_t kBacklightPin = 8;   // PA8 замість фатального PA13

void blink(const mcu::Pin& led, int times, std::chrono::milliseconds on,
           std::chrono::milliseconds off)
{
    for (int i = 0; i < times; ++i) {
        led.write(true);
        mcu::SystemClock::delay(on);
        led.write(false);
        mcu::SystemClock::delay(off);
    }
}

}  // namespace

int main()
{
    // Захисний інтервал — найперша дія. Усе нижче вже має право вмикати
    // периферію: налагоджувач своє вікно отримав.
    if (mcu::boot::guard(mcu::boot::kGuardWindow) == mcu::boot::GuardResult::HeldByOperator) {
        mcu::boot::park();
    }

    const auto clock = mcu::SystemClock::configure();

    // PA5 — індикатор. Перевірено на етапі компіляції, помилки тут бути не може.
    const mcu::Pin led = mcu::Pin::claim<mcu::Port::A, 5, kOutput>();

    // Та сама помилка, що вбиває першу партію плат: підсвічування дисплея
    // вішають на PA13. Рантайм-дорога відхиляє запит.
    //   mcu::Pin::claim<mcu::Port::A, 13, kOutput>();  // ← не збереться взагалі
    const auto backlight_on_swd = mcu::Pin::configure(mcu::Port::A, 13, kOutput);

    // Робочий вивід, який ні з чим системним не конфліктує.
    if (const auto backlight = mcu::Pin::configure(mcu::Port::A, kBacklightPin, kOutput)) {
        backlight->write(true);
    }

    // Свідоме перепризначення виглядає так: ключ, робота, автоматичне
    // повернення ліній шині налагодження на виході з області видимості.
    if (!backlight_on_swd && backlight_on_swd.error() == mcu::PinError::SwdPinLocked) {
        if (auto lease = mcu::SwdPinLease::acquire(mcu::kSwdUnlockKey)) {
            if (const auto probe = lease->configure(13, kOutput)) {
                probe->write(false);
                mcu::SystemClock::delay(1ms);
            }
        }   // деструктор оренди повернув PA13/PA14 у AF0
    }

    // Ритм індикатора одразу каже, на чому ми поїхали:
    //   один спалах на секунду — кварц і PLL живі,
    //   два коротких        — кварцу немає, PLL крутиться від HSI,
    //   три коротких        — тактування відкотилося на голий HSI.
    for (;;) {
        if (!clock) {
            blink(led, 3, 80ms, 160ms);
            mcu::SystemClock::delay(500ms);
        } else if (clock->source == mcu::ClockSource::HsePll) {
            blink(led, 1, 50ms, 950ms);
        } else {
            blink(led, 2, 80ms, 160ms);
            mcu::SystemClock::delay(500ms);
        }
    }
}
