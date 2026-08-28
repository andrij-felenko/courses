#include <cstdint>

/* Діагностичний аналізатор збою HardFault мовою C++ */
extern "C" void HardFault_Handler_C(std::uint32_t* stack_frame) {
    const std::uint32_t r0  = stack_frame[0];
    const std::uint32_t r1  = stack_frame[1];
    const std::uint32_t r2  = stack_frame[2];
    const std::uint32_t r3  = stack_frame[3];
    const std::uint32_t r12 = stack_frame[4];
    const std::uint32_t lr  = stack_frame[5];
    const std::uint32_t pc  = stack_frame[6]; /* Точна адреса аварійної інструкції */
    const std::uint32_t psr = stack_frame[7];

    const auto cfsr = *reinterpret_cast<volatile std::uint32_t*>(0xE000ED28UL);
    const auto hfsr = *reinterpret_cast<volatile std::uint32_t*>(0xE000ED2CUL);

    static_cast<void>(r0);  static_cast<void>(r1);  static_cast<void>(r2);
    static_cast<void>(r3);  static_cast<void>(r12); static_cast<void>(lr);
    static_cast<void>(pc);  static_cast<void>(psr); static_cast<void>(cfsr);
    static_cast<void>(hfsr);

    asm volatile("bkpt #0");
    while (true) {
    }
}
