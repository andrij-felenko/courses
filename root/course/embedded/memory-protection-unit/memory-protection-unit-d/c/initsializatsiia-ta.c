#include "cmsis_compiler.h"

void mpu_system_init_cmsis(void) {
    /* 1. Вимкнення MPU перед конфігурацією */
    ARM_MPU_Disable();

    /* 2. Регіон 0: Flash Код програми (0x08000000, 512 КБ, Unprivileged RO) */
    ARM_MPU_SetRegion(
        ARM_MPU_RBAR(0, 0x08000000),
        ARM_MPU_RASR(0, ARM_MPU_AP_URO, 0, 0, 1, 1, 0x00, ARM_MPU_REGION_SIZE_512KB)
    );

    /* 3. Регіон 1: Пам'ять ядра RTOS (0x20000000, 16 КБ, Privileged RW) */
    ARM_MPU_SetRegion(
        ARM_MPU_RBAR(1, 0x20000000),
        ARM_MPU_RASR(1, ARM_MPU_AP_PRIV, 0, 0, 1, 1, 0x00, ARM_MPU_REGION_SIZE_16KB)
    );

    /* 4. Регіон 2: Периферія MMIO (0x40000000, 512 МБ, Device Memory) */
    ARM_MPU_SetRegion(
        ARM_MPU_RBAR(2, 0x40000000),
        ARM_MPU_RASR(1, ARM_MPU_AP_PRIV, 2, 0, 0, 0, 0x00, ARM_MPU_REGION_SIZE_512MB)
    );

    /* 5. Регіон 3: Захисна зона NULL-покажчика (0x00000000, 32 Б, No Access) */
    ARM_MPU_SetRegion(
        ARM_MPU_RBAR(3, 0x00000000),
        ARM_MPU_RASR(1, ARM_MPU_AP_NONE, 0, 0, 0, 0, 0x00, ARM_MPU_REGION_SIZE_32B)
    );

    /* 6. Увімкнення винятку MemManage */
    SCB->SHCSR |= SCB_SHCSR_MEMFAULTENA_Msk;

    /* 7. Активація MPU з фоновою картою для ядра */
    ARM_MPU_Enable(MPU_CTRL_PRIVDEFENA_Msk);
}
