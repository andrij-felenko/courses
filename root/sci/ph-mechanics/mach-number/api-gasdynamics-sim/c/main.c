typedef struct {
    double true_airspeed_m_s;      /* Істинна повітряна швидкість v [м/с] */
    double mach_number;            /* Безрозмірне число Маха M = v / a */
    double total_temperature_k;     /* Повна температура гальмування T₀ [К] */
    double total_pressure_pa;       /* Повний тиск гальмування p₀ [Па] */
    double dynamic_pressure_pa;     /* Динамічний тиск (швидкісний напір) q [Па] */
    double prandtl_glauert_factor;    /* Поправка стисливості 1/√(1-M²) (для M < 1) */
    uint32_t flow_regime_flags;    /* Бітові прапорці режиму течії */
    uint32_t reserved;             /* Резервне поле для вирівнювання структури */
} compressible_flow_state_t;
