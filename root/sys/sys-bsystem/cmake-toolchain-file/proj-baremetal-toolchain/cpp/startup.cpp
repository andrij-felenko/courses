// startup.cpp — строго типізований стартап-код мовою C++ з викликом конструкторів
#include <cstdint>

extern "C" {
    extern std::uint32_t _estack;
    extern std::uint32_t _sidata, _sdata, _edata, _sbss, _ebss;
    extern void (*__init_array_start[])() noexcept;
    extern void (*__init_array_end[])() noexcept;
    void Reset_Handler() noexcept;
    void main_app() noexcept;
}

namespace {
[[noreturn]] void default_handler() noexcept {
    while (true) {}
}
}

using InterruptVector = void (*)() noexcept;

extern "C" [[gnu::section(".isr_vector")]]
const InterruptVector g_pfnVectors[] = {
    reinterpret_cast<InterruptVector>(&_estack),
    Reset_Handler,
    default_handler, // NMI
    default_handler  // HardFault
};

extern "C" void Reset_Handler() noexcept {
    // 1. Копіювання ініціалізованих змінних у RAM
    const auto *src = &_sidata;
    auto *dst = &_sdata;
    while (dst < &_edata) {
        *dst++ = *src++;
    }

    // 2. Очищення секції неініціалізованих змінних у RAM
    dst = &_sbss;
    while (dst < &_ebss) {
        *dst++ = 0;
    }

    // 3. Виклик конструкторів глобальних і статичних об'єктів C++
    for (auto **ctor = __init_array_start; ctor < __init_array_end; ++ctor) {
        if (*ctor != nullptr) {
            (*ctor)();
        }
    }

    // 4. Запуск головної логіки програми
    main_app();
    while (true) {}
}
