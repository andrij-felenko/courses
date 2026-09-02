#include "button_irq.hpp"

#include <atomic>

#include "gpio.hpp"

namespace {

constexpr std::uint32_t kLine = board::Button::PinT::kBit;  // PA0 -> лінія EXTI0
constexpr std::uint32_t kDebounceMs = 20;

using ExtiImr = mmio::Reg<soc::kExtiBase + 0x00>;
using ExtiRtsr = mmio::Reg<soc::kExtiBase + 0x08>;
using ExtiFtsr = mmio::Reg<soc::kExtiBase + 0x0C>;
using ExtiPr = mmio::Reg<soc::kExtiBase + 0x14>;
using AfioExticr1 = mmio::Reg<soc::kAfioBase + 0x08>;

using Tim3Cr1 = mmio::Reg<soc::kTim3Base + 0x00>;
using Tim3Dier = mmio::Reg<soc::kTim3Base + 0x0C>;
using Tim3Sr = mmio::Reg<soc::kTim3Base + 0x10>;
using Tim3Egr = mmio::Reg<soc::kTim3Base + 0x14>;
using Tim3Cnt = mmio::Reg<soc::kTim3Base + 0x24>;
using Tim3Psc = mmio::Reg<soc::kTim3Base + 0x28>;
using Tim3Arr = mmio::Reg<soc::kTim3Base + 0x2C>;
using NvicIser0 = mmio::Reg<soc::kNvicIser0>;

constexpr std::uint32_t kCr1Cen = 1u << 0;
constexpr std::uint32_t kCr1Urs = 1u << 2;
constexpr std::uint32_t kCr1Opm = 1u << 3;
constexpr std::uint32_t kUie = 1u << 0;
constexpr std::uint32_t kUif = 1u << 0;
constexpr std::uint32_t kUg = 1u << 0;

// Нуль — подій немає, далі значення ButtonEvent, зсунуте на одиницю.
// std::atomic<uint8_t> на Cortex-M3 вільний від блокувань, тому обмін із
// обробником переривання обходиться без гасіння переривань узагалі.
std::atomic<std::uint8_t> g_event{0};
std::atomic<bool> g_stablePressed{false};

void startOneShot() noexcept {
    Tim3Cnt::write(0);
    Tim3Sr::clearBits(kUif);
    Tim3Cr1::setBits(kCr1Cen);  // завдяки OPM таймер зупиниться сам
}

}  // namespace

namespace board {

void InterruptButton::start() noexcept {
    // Таймер блокування: один тик = 1 мс, один прохід на 20 мс.
    mmio::Reg<soc::kRccApb1Enr>::setBits(soc::kTim3En);
    Tim3Psc::write(soc::kCpuHz / 1000 - 1);
    Tim3Arr::write(kDebounceMs - 1);
    Tim3Cr1::write(kCr1Opm | kCr1Urs);
    Tim3Egr::write(kUg);        // переносимо PSC і ARR у тіньові регістри
    Tim3Sr::clearBits(kUif);    // подія UG підняла прапорець — знімаємо його
    Tim3Dier::setBits(kUie);
    NvicIser0::write(1u << soc::kTim3Irq);

    // Лінія EXTI0: джерело — порт A (нулі в молодшій тетраді EXTICR1).
    AfioExticr1::clearBits(0xFu);
    ExtiFtsr::setBits(kLine);   // натискання: фронт униз
    ExtiRtsr::setBits(kLine);   // відпускання: фронт угору
    ExtiPr::write(kLine);       // скидаємо сміття, накопичене при налаштуванні

    g_stablePressed.store(Button::isPressed(), std::memory_order_relaxed);
    g_event.store(0, std::memory_order_relaxed);

    ExtiImr::setBits(kLine);
    NvicIser0::write(1u << soc::kExti0Irq);
}

std::optional<ButtonEvent> InterruptButton::takeEvent() noexcept {
    const std::uint8_t raw = g_event.exchange(0, std::memory_order_acquire);
    if (raw == 0) {
        return std::nullopt;
    }
    return static_cast<ButtonEvent>(raw - 1);
}

}  // namespace board

// Імена обробників беруться з таблиці векторів стандартного startup-файлу,
// тому вони мусять мати сишне зв'язування — без extern "C" лінкер побачить
// перекручене ім'я, а вектор лишиться з обробником-заглушкою.
extern "C" void EXTI0_IRQHandler() {
    ExtiPr::write(kLine);       // прапорець знімається записом одиниці
    ExtiImr::clearBits(kLine);  // глушимо лінію на час брязкоту
    startOneShot();
}

extern "C" void TIM3_IRQHandler() {
    if ((Tim3Sr::read() & kUif) == 0u) {
        return;  // не наше джерело: інші канали лишаємо їхнім власникам
    }
    Tim3Sr::clearBits(kUif);

    const bool pressed = board::Button::isPressed();
    if (pressed != g_stablePressed.load(std::memory_order_relaxed)) {
        g_stablePressed.store(pressed, std::memory_order_relaxed);
        const auto ev = pressed ? board::ButtonEvent::Pressed : board::ButtonEvent::Released;
        g_event.store(static_cast<std::uint8_t>(static_cast<std::uint8_t>(ev) + 1),
                      std::memory_order_release);
    }
    // Якщо рівень повернувся до попереднього, події немає взагалі: спрацював не
    // контакт, а завада — і вона щойно коштувала нам двох переривань.

    // Поки лінія була замаскована, EXTI устиг записати в PR десятки фронтів.
    // Знімаємо їх ДО зняття маски, інакше контролер миттєво викличе обробник
    // ще раз, і весь антибрязкіт піде намарне.
    ExtiPr::write(kLine);
    ExtiImr::setBits(kLine);
}
