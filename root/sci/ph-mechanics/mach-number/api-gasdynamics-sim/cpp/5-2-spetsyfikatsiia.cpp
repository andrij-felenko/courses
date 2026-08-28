namespace gas_dynamics {

enum class regime_flags : std::uint32_t {
    subsonic_incompressible  = (1U << 0), // M < 0.3
    subsonic_compressible    = (1U << 1), // 0.3 <= M < 0.8
    transonic                = (1U << 2), // 0.8 <= M <= 1.2
    supersonic               = (1U << 3), // 1.2 < M <= 5.0
    hypersonic               = (1U << 4), // M > 5.0
    shock_wave_present       = (1U << 5), // Скачки ущільнення
    thermal_effects_critical = (1U << 6)  // Нагрів T0 > 500 K
};

} // namespace gas_dynamics
