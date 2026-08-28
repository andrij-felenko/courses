// startup_cortexm.cpp — типовий стартовий файл на C++20
#include <cstdint>
#include <array>

extern "C" {

using isr_handler_t = void (*)();

extern std::uint32_t _estack;
void Reset_Handler() noexcept;

// Спільна аварійна пастка
void Default_Handler() noexcept
{
    while (true) {
        #if defined(__arm__) || defined(__aarch64__)
        __asm__ volatile("wfi");
        #endif
    }
}

// Оголошення слабких псевдонімів
void NMI_Handler() noexcept [[gnu::weak, gnu::alias("Default_Handler")]];
void HardFault_Handler() noexcept [[gnu::weak, gnu::alias("Default_Handler")]];
void SysTick_Handler() noexcept [[gnu::weak, gnu::alias("Default_Handler")]];
void USART1_IRQHandler() noexcept [[gnu::weak, gnu::alias("Default_Handler")]];
void TIM2_IRQHandler() noexcept [[gnu::weak, gnu::alias("Default_Handler")]];

// Таблиця векторів
[[gnu::section(".isr_vector"), gnu::used]]
const std::array<isr_handler_t, 14> g_vector_table = {
    reinterpret_cast<isr_handler_t>(&_estack),
    Reset_Handler,
    NMI_Handler,
    HardFault_Handler,
    nullptr, nullptr, nullptr, nullptr, nullptr, nullptr, nullptr,
    SysTick_Handler,
    USART1_IRQHandler,
    TIM2_IRQHandler
};

} // extern "C"
