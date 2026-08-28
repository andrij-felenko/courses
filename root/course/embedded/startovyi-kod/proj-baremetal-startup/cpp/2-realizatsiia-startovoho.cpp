#include <cstdint>
#include <cstddef>
#include <span>

/* Символи меж від лінкера */
extern "C" {
    extern std::uint32_t _estack;
    extern std::uint32_t _sidata;
    extern std::uint32_t _sdata;
    extern std::uint32_t _edata;
    extern std::uint32_t _sbss;
    extern std::uint32_t _ebss;

    using CtorPointer = void (*)(void);
    extern CtorPointer __init_array_start[];
    extern CtorPointer __init_array_end[];

    int main();
    void Reset_Handler();
    void Default_Handler();

    void NMI_Handler()        __attribute__((weak, alias("Default_Handler")));
    void HardFault_Handler()  __attribute__((weak, alias("Default_Handler")));
    void MemManage_Handler()  __attribute__((weak, alias("Default_Handler")));
    void BusFault_Handler()   __attribute__((weak, alias("Default_Handler")));
    void UsageFault_Handler() __attribute__((weak, alias("Default_Handler")));
    void SVC_Handler()        __attribute__((weak, alias("Default_Handler")));
    void PendSV_Handler()     __attribute__((weak, alias("Default_Handler")));
    void SysTick_Handler()    __attribute__((weak, alias("Default_Handler")));
    void SystemInit()         __attribute__((weak));
}

void SystemInit() {
    /* Базова реалізація за замовчуванням */
}

namespace mcu::startup {
    /* Увімкнення апаратного співпроцесора FPU */
    inline void enable_fpu() noexcept {
        constexpr auto cpacr_reg_addr = static_cast<std::uintptr_t>(0xE000ED88UL);
        auto* const scb_cpacr = reinterpret_cast<volatile std::uint32_t*>(cpacr_reg_addr);
        
        constexpr std::uint32_t full_access = (0xFUL << 20);
        *scb_cpacr |= full_access;
        asm volatile("dsb\n\tisb" ::: "memory");
    }

    /* Виклик глобальних конструкторів через std::span */
    inline void call_constructors() noexcept {
        const std::span<CtorPointer> ctors(
            __init_array_start,
            static_cast<std::size_t>(__init_array_end - __init_array_start)
        );

        for (const auto ctor : ctors) {
            if (ctor != nullptr) {
                ctor();
            }
        }
    }
}

extern "C" void Reset_Handler() {
    /* 1. Копіювання ініціалізованих даних .data з Flash у RAM */
    const std::uint32_t* src = &_sidata;
    std::uint32_t* dst = &_sdata;
    while (dst < &_edata) {
        *dst++ = *src++;
    }

    /* 2. Заповнення секції .bss нулями в RAM */
    std::uint32_t* bss = &_sbss;
    while (bss < &_ebss) {
        *bss++ = 0;
    }

    /* 3. Апаратна ініціалізація ядра */
    mcu::startup::enable_fpu();
    SystemInit();

    /* 4. Запуск глобальних конструкторів C++ */
    mcu::startup::call_constructors();

    /* 5. Виклик прикладної логіки */
    static_cast<void>(main());

    /* 6. Термінальна енергозберігаюча пастка */
    while (true) {
        asm volatile("wfi");
    }
}

extern "C" void Default_Handler() {
    asm volatile("bkpt #0");
    while (true) {
    }
}

/* Типізована векторна таблиця для C++ */
using VectorEntry = void (*)(void);

extern "C" {
    __attribute__((section(".isr_vector"), used))
    const VectorEntry g_pfnVectors[] = {
        reinterpret_cast<VectorEntry>(&_estack),
        Reset_Handler,
        NMI_Handler,
        HardFault_Handler,
        MemManage_Handler,
        BusFault_Handler,
        UsageFault_Handler,
        nullptr, nullptr, nullptr, nullptr,
        SVC_Handler,
        nullptr,
        nullptr,
        PendSV_Handler,
        SysTick_Handler,
    };
}
