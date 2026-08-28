// weak_forms.cpp — еквівалентна ідіоматична реалізація для C++20
#include <iostream>
#include <string_view>
#include <cstdint>

// У C++ через спотворення імен (name mangling) для взаємодії з таблицями векторів
// та системним лінкером слабкі функції зазвичай експортують через extern "C".

extern "C" {

// 1. Слабке визначення (Weak Definition)
[[gnu::weak]] void log_event(const char* msg)
{
    std::cout << "[DEFAULT LOG]: " << (msg ? msg : "") << '\n';
}

// 2. Базовий обробник пастки
void Default_Handler() noexcept
{
    while (true) {
        #if defined(__x86_64__) || defined(_M_X64)
        __builtin_ia32_pause();
        #elif defined(__arm__) || defined(__aarch64__)
        __asm__ volatile("wfi");
        #endif
    }
}

// Слабкі псевдоніми через синтаксис атрибутів GNU
void SysTick_Handler() noexcept [[gnu::weak, gnu::alias("Default_Handler")]];
void USART1_IRQHandler() noexcept [[gnu::weak, gnu::alias("Default_Handler")]];

// 3. Слабке посилання
[[gnu::weak]] void hardware_crypto_init() noexcept;

} // extern "C"

namespace core::system {

void startup()
{
    log_event("Запуск підсистеми C++20...");

    // Перевірка наявності слабкого посилання в пам'яті
    if (hardware_crypto_init != nullptr) {
        hardware_crypto_init();
    } else {
        std::cout << "Криптомодуль відсутній, використовуємо софтверний fallback.\n";
    }
}

} // namespace core::system
