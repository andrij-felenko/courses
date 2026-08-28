namespace hardware {

struct MpuConfiguration {
    static constexpr std::uint32_t RegionSize64Bytes = 5; // 2^(5+1) = 64

    static void configure_noncacheable_region(void* base_address) noexcept {
        MPU->CTRL = 0;
        MPU->RNR = 0;
        MPU->RBAR = reinterpret_cast<std::uint32_t>(base_address) & MPU_RBAR_ADDR_Msk;
        MPU->RASR = (3 << MPU_RASR_AP_Pos) |
                    (1 << MPU_RASR_C_Pos)  |
                    (RegionSize64Bytes << MPU_RASR_SIZE_Pos) |
                    (1 << MPU_RASR_ENABLE_Pos);

        MPU->CTRL = MPU_CTRL_ENABLE_Msk | MPU_CTRL_PRIVDEFENA_Msk;
        __DSB();
        __ISB();
    }
};

} // namespace hardware
