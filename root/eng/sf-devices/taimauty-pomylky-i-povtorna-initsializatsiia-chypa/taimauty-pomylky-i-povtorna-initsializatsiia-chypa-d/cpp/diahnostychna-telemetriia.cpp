struct BusDiagnostics {
    uint32_t timeout_errors{0};
    uint32_t nack_errors{0};
    uint32_t bus_stuck_errors{0};
    uint32_t tier1_soft_resets{0};
    uint32_t tier2_pin_resets{0};
    uint32_t tier3_power_cycles{0};
    uint32_t crc_errors{0};
    uint32_t last_error_code{0};
};
