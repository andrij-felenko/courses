#include <stdint.h>
#include <stdbool.h>

// Опитування та декодування 8-бітного конфігураційного байта
typedef struct {
    uint8_t device_address; // Біти 0..2: адреса (0-7)
    uint8_t baud_rate_id;   // Біти 3..4: швидкість (0-3)
    bool dhcp_enabled;      // Біт 5: увімкнення DHCP
    bool parity_check;      // Біт 6: перевірка парності
} app_config_t;

app_config_t parse_dip_configuration(uint8_t raw_byte) {
    app_config_t cfg;
    // Оскільки конфігурація Pull-Up інверсна (active-LOW), інвертуємо байт
    uint8_t active_high_byte = ~raw_byte;
    
    cfg.device_address = active_high_byte & 0x07;         // Маска 0b00000111
    cfg.baud_rate_id   = (active_high_byte >> 3) & 0x03;  // Маска 0b00000011 зсунута на 3
    cfg.dhcp_enabled   = (active_high_byte >> 5) & 0x01;  // Маска 0b00000001 зсунута на 5
    cfg.parity_check   = (active_high_byte >> 6) & 0x01;  // Маска 0b00000001 зсунута на 6
    
    return cfg;
}
