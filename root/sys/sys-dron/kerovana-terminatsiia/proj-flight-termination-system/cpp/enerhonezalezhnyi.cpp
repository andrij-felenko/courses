namespace fts::embedded {

enum class TriggerReason : uint8_t {
    ManualCommand = 1,
    TumblingSpin  = 2,
    LinkTimeout   = 3
};

struct [[gnu::packed]] BlackboxRecord {
    uint32_t      crash_magic{0xDEADF751U};
    uint32_t      crash_timestamp_ms{0};
    TriggerReason trigger_reason{TriggerReason::ManualCommand};
    State         fsm_state_at_crash{State::Safe};
    uint16_t      battery_voltage_mv{0};
    float         last_spin_rate{0.0F};
    float         last_accel_g{0.0F};
    uint32_t      last_radio_seq{0};
    uint32_t      crc32{0};
};

} // namespace fts::embedded
