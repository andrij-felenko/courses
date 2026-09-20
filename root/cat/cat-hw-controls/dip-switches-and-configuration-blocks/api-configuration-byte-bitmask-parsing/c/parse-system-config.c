#include <stdint.h>
#include <stdbool.h>

typedef struct {
    uint8_t i2c_address;     // Біти 0..2 (адреса 0x30..0x37)
    uint8_t baudrate_index;  // Біти 3..4 (індекс швидкості 0..3)
    bool debug_mode_enabled; // Біт 5 (прапорець відлагодження)
    bool is_valid;           // Прапорець успішної валідації
} system_config_t;

system_config_t parse_system_config(uint8_t debounced_byte) {
    system_config_t config;

    // Витягнення бітових полів
    uint8_t raw_addr = extract_bitfield(debounced_byte, 0, 3);
    uint8_t raw_baud = extract_bitfield(debounced_byte, 3, 2);
    uint8_t raw_dbg  = extract_bitfield(debounced_byte, 5, 1);

    // Валідація та мапінг
    config.i2c_address = 0x30U + raw_addr; // Адреси 0x30..0x37
    config.baudrate_index = raw_baud;
    config.debug_mode_enabled = (raw_dbg != 0);
    config.is_valid = (raw_baud <= 3);      // Перевірка допустимого індексу

    return config;
}
