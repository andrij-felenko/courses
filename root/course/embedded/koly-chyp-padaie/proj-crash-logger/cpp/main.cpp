#include <cstdint>
#include <cstddef>
#include <span>
#include <string_view>
#include "stm32f4xx.h"

namespace crash::handler {

struct alignas(4) StackFrame {
    uint32_t r0;
    uint32_t r1;
    uint32_t r2;
    uint32_t r3;
    uint32_t r12;
    uint32_t lr;
    uint32_t pc;
    uint32_t psr;
};

struct alignas(4) DumpRecord {
    uint32_t magic;
    uint32_t crash_count;
    uint32_t reset_reason;
    uint32_t hfsr;
    uint32_t cfsr;
    uint32_t mmfar;
    uint32_t bfar;
    uint32_t shcsr;
    uint32_t exc_return;
    StackFrame frame;
    uint32_t crc;
};

inline constexpr uint32_t MagicKey = 0xDEADBEEF;
inline constexpr uint32_t MaxCrashThreshold = 3;

// Розміщення в .noinit пам'яті
__attribute__((section(".noinit")))
inline volatile DumpRecord g_retained_dump;

[[nodiscard]] constexpr uint32_t compute_crc32(std::span<const uint8_t> data) noexcept {
    uint32_t crc = 0xFFFFFFFF;
    for (uint8_t byte : data) {
        crc ^= byte;
        for (size_t bit = 0; bit < 8; ++bit) {
            crc = (crc & 1) ? ((crc >> 1) ^ 0xEDB88320) : (crc >> 1);
        }
    }
    return ~crc;
}

inline void uart_transmit_blocking(std::string_view text) noexcept {
    for (char c : text) {
        while (!(USART1->SR & USART_SR_TXE)) {}
        USART1->DR = static_cast<uint8_t>(c);
    }
}

extern "C" void HardFault_Handler_Cpp(const StackFrame *frame, uint32_t exc_return) noexcept {
    const uint32_t count = (g_retained_dump.magic == MagicKey) ? g_retained_dump.crash_count + 1 : 1;

    g_retained_dump.magic = MagicKey;
    g_retained_dump.crash_count = count;
    g_retained_dump.reset_reason = RCC->CSR;
    g_retained_dump.hfsr = SCB->HFSR;
    g_retained_dump.cfsr = SCB->CFSR;
    g_retained_dump.mmfar = SCB->MMFAR;
    g_retained_dump.bfar = SCB->BFAR;
    g_retained_dump.shcsr = SCB->SHCSR;
    g_retained_dump.exc_return = exc_return;

    if (frame != nullptr) {
        g_retained_dump.frame = *frame;
    }

    const auto dump_bytes = std::span<const uint8_t>(
        reinterpret_cast<const uint8_t*>(&g_retained_dump),
        sizeof(DumpRecord) - sizeof(uint32_t)
    );
    g_retained_dump.crc = compute_crc32(dump_bytes);

    uart_transmit_blocking("\r\n[CRASH] Hardware fault captured, rebooting...\r\n");

    NVIC_SystemReset();
}

[[nodiscard]] inline bool process_retained_dump() noexcept {
    if (g_retained_dump.magic != MagicKey) {
        return false;
    }

    const auto dump_bytes = std::span<const uint8_t>(
        reinterpret_cast<const uint8_t*>(&g_retained_dump),
        sizeof(DumpRecord) - sizeof(uint32_t)
    );

    if (compute_crc32(dump_bytes) != g_retained_dump.crc) {
        g_retained_dump.magic = 0;
        return false;
    }

    if (g_retained_dump.crash_count >= MaxCrashThreshold) {
        uart_transmit_blocking("[CRASH-LOOP] Too many crashes! Safe boot engaged.\r\n");
    }

    g_retained_dump.magic = 0;
    return true;
}

} // namespace crash::handler

// Асемблерний трамплін
extern "C" __attribute__((naked)) void HardFault_Handler(void) {
    __asm volatile(
        "tst lr, #4                \n"
        "ite eq                    \n"
        "mrseq r0, msp             \n"
        "mrsne r0, psp             \n"
        "mov r1, lr                \n"
        "b HardFault_Handler_Cpp   \n"
    );
}
