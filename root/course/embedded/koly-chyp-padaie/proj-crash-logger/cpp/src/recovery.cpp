#include "recovery.hpp"

#include <cstdint>

#include "crash_record.hpp"
#include "stm32f4xx.h"
#include "sync_uart.hpp"

namespace crash {
namespace {

using namespace std::chrono_literals;

using io::console::newline;
using io::console::write;
using io::console::write_dec;

constexpr std::uint32_t kCrashLoopThreshold = 3;
constexpr std::chrono::milliseconds kHealthyUptime = 60s;

// Плата курсу: дозвіл силових ключів — PB0, живлення радіомодуля — PB1.
constexpr unsigned kActuatorEnablePin = 0;
constexpr unsigned kRadioEnablePin = 1;

// Системний завантажувач STM32F4 (AN2606). В інших родин адреса своя.
constexpr std::uintptr_t kSystemBootloader = 0x1FFF'0000;

bool g_counter_cleared = false;

// Приводи й радіо гасимо ПЕРШИМИ: у безпечний режим ми потрапили тому, що
// прошивка падає, а мотор під живленням встигне наробити біди.
void shutdown_outputs() noexcept
{
    RCC->AHB1ENR |= RCC_AHB1ENR_GPIOBEN;

    const std::uint32_t mode_mask =
        (3u << (kActuatorEnablePin * 2)) | (3u << (kRadioEnablePin * 2));
    GPIOB->MODER = (GPIOB->MODER & ~mode_mask) |
                   ((1u << (kActuatorEnablePin * 2)) | (1u << (kRadioEnablePin * 2)));
    GPIOB->BSRR = (1u << (kActuatorEnablePin + 16)) | (1u << (kRadioEnablePin + 16));
}

[[noreturn]] void jump_to_system_bootloader() noexcept
{
    using EntryFn = void (*)();

    __disable_irq();

    // Гасимо все, що могло б вистрілити перериванням уже всередині завантажувача.
    SysTick->CTRL = 0;
    SysTick->LOAD = 0;
    SysTick->VAL = 0;
    for (auto& reg : NVIC->ICER) {
        reg = 0xFFFF'FFFF;
    }
    for (auto& reg : NVIC->ICPR) {
        reg = 0xFFFF'FFFF;
    }

    const auto* vectors = reinterpret_cast<const volatile std::uint32_t*>(kSystemBootloader);
    const std::uint32_t stack_top = vectors[0];
    const auto entry = reinterpret_cast<EntryFn>(vectors[1]);

    SCB->VTOR = kSystemBootloader;
    __DSB();
    __ISB();
    __set_MSP(stack_top);
    __enable_irq();
    entry();

    while (true) {
    } // сюди не повертаються
}

} // namespace

BootDecision decide()
{
    const std::uint32_t crashes = consecutive();
    if (crashes == 0) {
        return BootDecision::Normal;
    }

    static_cast<void>(write("[guard] падінь поспіль: "));
    static_cast<void>(write_dec(crashes));
    static_cast<void>(write(" з "));
    static_cast<void>(write_dec(kCrashLoopThreshold));
    static_cast<void>(newline());

    return crashes >= kCrashLoopThreshold ? BootDecision::SafeMode : BootDecision::Normal;
}

void note_uptime(std::chrono::milliseconds uptime)
{
    if (g_counter_cleared || uptime < kHealthyUptime) {
        return;
    }
    g_counter_cleared = true;
    if (consecutive() > 0) {
        clear_counter();
        static_cast<void>(write("[guard] хвилина без падінь — лічильник скинуто\r\n"));
    }
}

void safe_mode()
{
    shutdown_outputs();

    static_cast<void>(
        write("\r\n[safe] аварійний режим: приводи знеструмлено, задачі не стартують\r\n"));
    static_cast<void>(
        write("[safe] r - перезапуск, c - скинути лічильник, b - завантажувач\r\n"));

    while (true) {
        const auto cmd = io::console::read();
        if (!cmd) {
            continue;
        }
        switch (*cmd) {
        case 'r':
            NVIC_SystemReset();
            break;
        case 'c':
            clear_counter();
            static_cast<void>(write("[safe] лічильник скинуто\r\n"));
            NVIC_SystemReset();
            break;
        case 'b':
            static_cast<void>(write("[safe] стрибок у системний завантажувач\r\n"));
            jump_to_system_bootloader();
        default:
            static_cast<void>(write("[safe] невідома команда\r\n"));
            break;
        }
    }
}

} // namespace crash
