#include "button_irq.hpp"
#include "debouncer.hpp"
#include "gpio.hpp"

namespace {

// Обидва підходи керують тією самою ніжкою PA0, тому в прошивці живе рівно
// один: false — періодичне опитування із SysTick, true — EXTI з таймером.
constexpr bool kUseInterruptDebounce = false;

using SysTickCtrl = mmio::Reg<soc::kSysTickBase + 0x00>;
using SysTickLoad = mmio::Reg<soc::kSysTickBase + 0x04>;
using SysTickVal = mmio::Reg<soc::kSysTickBase + 0x08>;

board::Debouncer<5> g_button{};
volatile std::uint32_t g_pressCount{0};

void startTick10ms() noexcept {
    // 8 МГц / 100 = 80000 тактів; у регістрі лежить N-1, і 79999 вміщається
    // у 24-бітний лічильник ядра.
    SysTickLoad::write(soc::kCpuHz / 100 - 1);
    SysTickVal::write(0);  // запис будь-якого значення скидає лічильник і прапорець
    SysTickCtrl::write(0b111);  // CLKSOURCE=HCLK, TICKINT, ENABLE
}

void onPress() noexcept {
    ++g_pressCount;
    board::Led::toggle();
}

}  // namespace

extern "C" void SysTick_Handler() {
    // Раз на 10 мс. Ніяких затримок усередині: обробник має піти з ядра за
    // одиниці мікросекунд, інакше він з'їсть переривання решти периферії.
    if (g_button.update(board::Button::isPressed()) == board::ButtonEvent::Pressed) {
        onPress();
    }
}

int main() {
    board::Led::init();
    board::Button::init();

    if constexpr (kUseInterruptDebounce) {
        board::InterruptButton::start();
    } else {
        g_button = board::Debouncer<5>{board::Button::isPressed()};
        startTick10ms();
    }

    while (true) {
        if constexpr (kUseInterruptDebounce) {
            if (board::InterruptButton::takeEvent() == board::ButtonEvent::Pressed) {
                onPress();
            }
        }
        // Ядро спить до наступного переривання: в опитуванні його будить
        // SysTick, у варіанті з EXTI — сама кнопка.
        __asm volatile("wfi");
    }
}
