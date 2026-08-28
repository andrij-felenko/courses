// core/src/startup_stm32f407xx.cpp
#include <cstdint>
#include <span>

extern "C" {
    extern std::uint32_t _estack;
    extern std::uint32_t _sidata;
    extern std::uint32_t _sdata;
    extern std::uint32_t _edata;
    extern std::uint32_t _sbss;
    extern std::uint32_t _ebss;

    void SystemInit() noexcept;
    void __libc_init_array() noexcept;
    int main();

    void Reset_Handler() noexcept;
    void Default_Handler() noexcept {
        while (true) {}
    }

    void NMI_Handler() noexcept       [[gnu::weak, gnu::alias("Default_Handler")]];
    void HardFault_Handler() noexcept [[gnu::weak, gnu::alias("Default_Handler")]];
    void SysTick_Handler() noexcept   [[gnu::weak, gnu::alias("Default_Handler")]];

    using IsrVectorFn = void (*)(void);

    [[gnu::section(".isr_vector"), gnu::used]]
    const IsrVectorFn g_pfnVectors[] = {
        reinterpret_cast<IsrVectorFn>(&_estack),
        Reset_Handler,
        NMI_Handler,
        HardFault_Handler,
        nullptr, nullptr, nullptr, nullptr, nullptr, nullptr, nullptr,
        nullptr, nullptr, nullptr,
        SysTick_Handler
    };
}

void Reset_Handler() noexcept {
    // 1. Копіювання секції .data
    const auto* src = &_sidata;
    auto* dst = &_sdata;
    while (dst < &_edata) {
        *dst++ = *src++;
    }

    // 2. Очищення секції .bss
    dst = &_sbss;
    while (dst < &_ebss) {
        *dst++ = 0;
    }

    // 3. Ініціалізація ядра та виклик конструкторів
    SystemInit();
    __libc_init_array();

    // 4. Головний цикл застосунку
    main();

    while (true) {}
}
