// startup.cpp — Ідіоматична стартова ініціалізація мовою C++20
#include <cstdint>
#include <span>
#include <algorithm>

// Експорт лінкерних символів через масиви без розміру
extern "C" {
    extern std::uint32_t _estack[];
    extern std::uint32_t _sidata[];
    extern std::uint32_t _sdata[];
    extern std::uint32_t _edata[];
    extern std::uint32_t _sbss[];
    extern std::uint32_t _ebss[];
    extern std::uint32_t _siccmram[];
    extern std::uint32_t _sccmram[];
    extern std::uint32_t _eccmram[];

    void Reset_Handler() noexcept;
    void Default_Handler() noexcept;
    void __libc_init_array() noexcept;
    int main();
}

// Псевдоніми обробників переривань
extern "C" {
    void NMI_Handler() __attribute__((weak, alias("Default_Handler")));
    void HardFault_Handler() __attribute__((weak, alias("Default_Handler")));
    void SysTick_Handler() __attribute__((weak, alias("Default_Handler")));
}

// Типобезпечна таблиця векторів переривань
using VectorHandler = void (*)();

struct VectorTable {
    const void* initial_sp;
    VectorHandler reset;
    VectorHandler nmi;
    VectorHandler hard_fault;
    VectorHandler reserved[4];
    VectorHandler sv_call;
    VectorHandler reserved_debug;
    VectorHandler reserved2;
    VectorHandler pend_sv;
    VectorHandler sys_tick;
};

__attribute__((section(".isr_vector"), used))
const VectorTable g_vector_table = {
    .initial_sp = _estack,
    .reset = Reset_Handler,
    .nmi = NMI_Handler,
    .hard_fault = HardFault_Handler,
    .reserved = {nullptr, nullptr, nullptr, nullptr},
    .sv_call = nullptr,
    .reserved_debug = nullptr,
    .reserved2 = nullptr,
    .pend_sv = nullptr,
    .sys_tick = SysTick_Handler
};

void Reset_Handler() noexcept {
    // 1. Копіювання секції .data за допомогою std::copy
    const auto data_size = reinterpret_cast<std::uintptr_t>(_edata) - reinterpret_cast<std::uintptr_t>(_sdata);
    const std::span<const std::uint32_t> data_flash{_sidata, data_size / sizeof(std::uint32_t)};
    const std::span<std::uint32_t> data_ram{_sdata, data_size / sizeof(std::uint32_t)};
    std::copy(data_flash.begin(), data_flash.end(), data_ram.begin());

    // 2. Обнулення секції .bss за допомогою std::fill
    const auto bss_size = reinterpret_cast<std::uintptr_t>(_ebss) - reinterpret_cast<std::uintptr_t>(_sbss);
    const std::span<std::uint32_t> bss_ram{_sbss, bss_size / sizeof(std::uint32_t)};
    std::fill(bss_ram.begin(), bss_ram.end(), 0U);

    // 3. Ініціалізація CCMRAM
    const auto ccm_size = reinterpret_cast<std::uintptr_t>(_eccmram) - reinterpret_cast<std::uintptr_t>(_sccmram);
    if (ccm_size > 0) {
        const std::span<const std::uint32_t> ccm_flash{_siccmram, ccm_size / sizeof(std::uint32_t)};
        const std::span<std::uint32_t> ccm_ram{_sccmram, ccm_size / sizeof(std::uint32_t)};
        std::copy(ccm_flash.begin(), ccm_flash.end(), ccm_ram.begin());
    }

    // 4. Виклик конструкторів статичних і глобальних об'єктів
    __libc_init_array();

    // 5. Виклик main()
    main();

    while (true) {
        asm volatile("wfi");
    }
}

void Default_Handler() noexcept {
    while (true) {
        asm volatile("wfi");
    }
}
