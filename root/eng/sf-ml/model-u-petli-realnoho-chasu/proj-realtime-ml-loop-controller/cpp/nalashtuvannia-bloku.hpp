void configureMpuRegions() noexcept {
    ARM_MPU_Disable();

    // Регіон 0: DTCM (128 КБ) - Повний доступ, некешована нормальна пам'ять
    ARM_MPU_SetRegion(
        ARM_MPU_RBAR(0, 0x20000000),
        ARM_MPU_RASR(0, ARM_MPU_AP_FULL, ARM_MPU_ACCESS_NORMAL(ARM_MPU_ATTR_NON_CACHEABLE, ARM_MPU_ATTR_NON_CACHEABLE, 0), 0, 0, ARM_MPU_REGION_SIZE_128KB)
    );

    // Регіон 1: RAM_D3 (64 КБ) - Буфери обміну, Strongly-Ordered / Device
    ARM_MPU_SetRegion(
        ARM_MPU_RBAR(1, 0x38000000),
        ARM_MPU_RASR(0, ARM_MPU_AP_FULL, ARM_MPU_ACCESS_DEVICE(1), 0, 0, ARM_MPU_REGION_SIZE_64KB)
    );

    ARM_MPU_Enable(MPU_CTRL_PRIVDEFENA_Msk);
}
