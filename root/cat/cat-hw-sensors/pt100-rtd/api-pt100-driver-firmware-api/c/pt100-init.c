// Коди повернення статусів драйвера
typedef enum {
    PT100_OK = 0,
    PT100_ERR_COMMUNICATION,
    PT100_ERR_INVALID_PARAM,
    PT100_ERR_HARDWARE_FAULT
} pt100_status_t;

// Ініціалізація AFE та перевірка готовності апаратури
pt100_status_t pt100_init(const pt100_config_t *config) {
    if (config == NULL || config->r_ref_ohms <= 0.0f) {
        return PT100_ERR_INVALID_PARAM;
    }

    // Перевірка зв'язку з чіпом AFE (читання ID)
    uint8_t chip_id = 0;
    if (afe_read_register(0x00, &chip_id) != 0 || chip_id != 0x80) {
        return PT100_ERR_COMMUNICATION;
    }

    // Запис регістра конфігурації AFE (струм збудження, схема дротів, фільтр 50/60 Гц)
    uint8_t conf_reg = (config->wire_mode == PT100_WIRE_3) ? 0x10 : 0x00;
    if (afe_write_register(0x01, conf_reg) != 0) {
        return PT100_ERR_HARDWARE_FAULT;
    }

    return PT100_OK;
}
