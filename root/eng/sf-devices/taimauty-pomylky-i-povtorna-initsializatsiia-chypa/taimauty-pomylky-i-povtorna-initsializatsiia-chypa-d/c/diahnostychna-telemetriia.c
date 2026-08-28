typedef struct {
    uint32_t timeout_errors;        // Кількість таймаутів очікування прапорців
    uint32_t nack_errors;           // Кількість неотриманих підтверджень ACK
    uint32_t bus_stuck_errors;      // Кількість виявлених блокувань SDA=0
    uint32_t tier1_soft_resets;     // Кількість виконаних програмних скидань
    uint32_t tier2_pin_resets;      // Кількість апаратних імпульсів nRESET
    uint32_t tier3_power_cycles;    // Кількість повних циклів живлення
    uint32_t crc_errors;            // Кількість помилок контрольних сум даних
    uint32_t last_error_code;       // Код останньої зафіксованої помилки
} bus_diagnostics_t;
