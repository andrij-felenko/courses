#include "cmsis_compiler.h"
#include <cstdint>

class CmsisMpuController {
public:
    static void initialize() noexcept {
        ARM_MPU_Disable();

        configure_region(0, 0x08000000, ARM_MPU_AP_URO,  0, true,  ARM_MPU_REGION_SIZE_512KB);
        configure_region(1, 0x20000000, ARM_MPU_AP_PRIV, 0, false, ARM_MPU_REGION_SIZE_16KB);
        configure_region(2, 0x40000000, ARM_MPU_AP_PRIV, 2, false, ARM_MPU_REGION_SIZE_512MB);
        configure_region(3, 0x00000000, ARM_MPU_AP_NONE, 0, false, ARM_MPU_REGION_SIZE_32B);

        SCB->SHCSR |= SCB_SHCSR_MEMFAULTENA_Msk;
        ARM_MPU_Enable(MPU_CTRL_PRIVDEFENA_Msk);
    }

private:
    static void configure_region(uint32_t region_num, uint32_t base_addr, 
                                 uint8_t ap, uint8_t tex, bool exec, uint8_t size_code) noexcept {
        ARM_MPU_SetRegion(
            ARM_MPU_RBAR(region_num, base_addr),
            ARM_MPU_RASR(!exec, ap, tex, 0, 1, 1, 0x00, size_code)
        );
    }
};
