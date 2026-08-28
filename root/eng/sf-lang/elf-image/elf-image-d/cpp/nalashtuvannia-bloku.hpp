#include <cstdint>

namespace mpu {

struct MpuRegisters {
    volatile std::uint32_t type;
    volatile std::uint32_t ctrl;
    volatile std::uint32_t rnr;
    volatile std::uint32_t rbar;
    volatile std::uint32_t rasr;
};

inline auto* const Regs = reinterpret_cast<MpuRegisters*>(0xE000ED90);

void setup_memory_protection() noexcept {
    Regs->ctrl = 0; // Вимкнення MPU на час переналаштування

    // Регіон 0: Flash пам'ять (ReadOnly, Executable, 512KB)
    Regs->rnr  = 0;
    Regs->rbar = 0x08000000U | 0x10U;
    Regs->rasr = (0U << 28) | (2U << 24) | (18U << 1) | 1U;

    // Регіон 1: SRAM пам'ять (ReadWrite, Execute-Never, 128KB)
    Regs->rnr  = 1;
    Regs->rbar = 0x20000000U | 0x10U;
    Regs->rasr = (1U << 28) | (3U << 24) | (16U << 1) | 1U;

    // Увімкнення MPU
    Regs->ctrl = 0x05U;

    #if defined(__arm__) || defined(__thumb__)
    asm volatile("dsb 0xF\nisb 0xF" ::: "memory");
    #endif
}

} // namespace mpu
