#include <cstdint>

namespace mpu {

struct HardwareMpu {
    volatile std::uint32_t type;
    volatile std::uint32_t ctrl;
    volatile std::uint32_t rnr;
    volatile std::uint32_t rbar;
    volatile std::uint32_t rasr;
};

inline auto& hardware_mpu = *reinterpret_cast<HardwareMpu*>(0xE000ED90);

void setup_non_cacheable_d2_region() noexcept {
    hardware_mpu.ctrl = 0; // Вимкнути MPU перед модифікацією

    hardware_mpu.rnr = 0;             // Регіон № 0
    hardware_mpu.rbar = 0x30000000U;  // Базова адреса RAM_D2

    // XN=1, AP=RW (3), Non-cacheable (TEX=1, C=0, B=0), Size=512KB (18), Enable=1
    constexpr std::uint32_t rasr_config = 
        (1U << 28) | (3U << 24) | (1U << 19) | (18U << 1) | 1U;
    hardware_mpu.rasr = rasr_config;

    // Увімкнути MPU з бітом PRIVDEFENA (фонова адресація для решти Flash/RAM)
    hardware_mpu.ctrl = (1U << 2) | (1U << 0);

    asm volatile("dsb 0xf\nisb 0xf" ::: "memory");
}

} // namespace mpu
