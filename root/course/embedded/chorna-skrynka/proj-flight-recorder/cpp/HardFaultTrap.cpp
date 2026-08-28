// HardFaultTrap.cpp - Перехоплювач аварійних винятків (C++20)
#include "FlightRecorderCore.hpp"

extern "C" void prvGetRegistersFromStackCpp(uint32_t* stack_frame) noexcept {
    const uint32_t pc = stack_frame[6];
    const auto cfsr = *reinterpret_cast<volatile uint32_t*>(0xE000ED28);
    const auto bfar = *reinterpret_cast<volatile uint32_t*>(0xE000ED38);

    // Звернення до глобального екземпляра реєстратора
    extern embedded::diagnostics::FlightRecorderEngine<256> g_flight_recorder;
    g_flight_recorder.emergency_panic(static_cast<uint8_t>(cfsr & 0xFF), pc, bfar);

    // Ініціація рестарту ядра
    auto* const aircr = reinterpret_cast<volatile uint32_t*>(0xE000ED0C);
    *aircr = 0x05FA0000U | (1U << 2);
    while (true) { asm volatile("nop"); }
}

extern "C" [[gnu::naked]] void HardFault_Handler() noexcept {
    asm volatile(
        "tst lr, #4\n"
        "ite eq\n"
        "mrseq r0, msp\n"
        "mrsne r0, psp\n"
        "b prvGetRegistersFromStackCpp\n"
    );
}
