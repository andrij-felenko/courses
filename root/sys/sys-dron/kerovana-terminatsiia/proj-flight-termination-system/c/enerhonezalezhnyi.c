typedef struct __attribute__((packed)) {
    uint32_t crash_magic;        /* 0xDEADF751 */
    uint32_t crash_timestamp_ms; /* Час спрацьовування */
    uint8_t  trigger_reason;     /* 1: Ручна команда, 2: Штопор, 3: Таймаут */
    uint8_t  fsm_state_at_crash; /* Стан автомата FSM */
    uint16_t battery_voltage_mv; /* Напруга резервної батареї */
    float    last_spin_rate;     /* Зафіксована кутова швидкість, рад/с */
    float    last_accel_g;       /* Зафіксоване перевантаження, g */
    uint32_t last_radio_seq;     /* Останній прийнятий номер пакета */
    uint32_t crc32;              /* Контрольна сума запису */
} fts_blackbox_record_t;
