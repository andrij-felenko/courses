#include <cstdint>
#include <cstddef>

struct MpuRegisters {
    volatile uint32_t TYPE;
    volatile uint32_t CTRL;
    volatile uint32_t RNR;
    volatile uint32_t RBAR;
    volatile uint32_t RASR;
};

class MpuConfigurator {
    inline static auto* const MPU = reinterpret_cast<MpuRegisters*>(0xE000ED90);

public:
    static void configure_non_cacheable_region(uint32_t base_addr, uint8_t region_number, uint8_t size_exponent) noexcept {
        asm volatile ("dmb" ::: "memory");
        MPU->CTRL = 0;

        MPU->RNR = region_number;
        MPU->RBAR = base_addr;

        const uint32_t rasr = (1u << 28) |               // XN: Execute Never
                             (0x3u << 24) |             // AP: Read/Write Privileged & Unprivileged
                             (0x1u << 19) |             // TEX: 001 (Normal Non-Cacheable)
                             (0u << 17) |               // C: 0
                             (0u << 16) |               // B: 0
                             (1u << 18) |               // S: 1 (Shareable)
                             (static_cast<uint32_t>(size_exponent - 1) << 1) |
                             (1u << 0);                 // Enable region

        MPU->RASR = rasr;
        MPU->CTRL = (1u << 2) | (1u << 0); // PRIVDEFENA | ENABLE

        asm volatile ("dsb" ::: "memory");
        asm volatile ("isb" ::: "memory");
    }
};
