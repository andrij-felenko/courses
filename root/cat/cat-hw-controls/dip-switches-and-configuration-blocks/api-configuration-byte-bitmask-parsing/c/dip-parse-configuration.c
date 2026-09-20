#include <stdint.h>
#include <stdbool.h>

#define MAX_VALID_MODES 5

typedef enum {
    DIP_PARSE_OK = 0,
    DIP_PARSE_ERR_INVALID_MODE = 1
} dip_parse_status_t;

typedef struct {
    uint8_t i2c_address;     // Суб-поле b0...b3 (0..15)
    uint8_t operation_mode;  // Суб-поле b4...b6 (0..4)
    bool    turbo_enabled;   // Прапорець b7
    dip_parse_status_t status;
} dip_parsed_config_t;

// Повний цикл розпаршування та валідації конфігураційного байта
dip_parsed_config_t dip_parse_configuration(uint8_t norm_byte) {
    dip_parsed_config_t cfg;
    cfg.i2c_address = dip_extract_field(norm_byte, 4, 0);
    
    uint8_t raw_mode = dip_extract_field(norm_byte, 3, 4);
    if (raw_mode < MAX_VALID_MODES) {
        cfg.operation_mode = raw_mode;
        cfg.status = DIP_PARSE_OK;
    } else {
        cfg.operation_mode = 0; // Встановлення безпечного резервного стану (fallback state)
        cfg.status = DIP_PARSE_ERR_INVALID_MODE;
    }
    
    cfg.turbo_enabled = dip_extract_flag(norm_byte, 7);
    return cfg;
}
