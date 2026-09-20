#include <stdint.h>
#include <stdbool.h>

#define THUMBWHEEL_MAX_DECADES  6

typedef enum {
    THUMBWHEEL_CODE_BCD_DIRECT = 0,
    THUMBWHEEL_CODE_BCD_COMPLEMENT,
    THUMBWHEEL_CODE_HEX
} thumbwheel_code_type_t;

typedef struct {
    uint8_t num_decades;
    thumbwheel_code_type_t code_type;
    bool active_low;
    uint8_t debounce_ticks;
    const uint8_t *scan_pins;
    const uint8_t *data_pins;
} thumbwheel_config_t;

typedef struct {
    uint8_t raw_code;
    uint8_t candidate_code;
    uint8_t debounced_code;
    uint8_t stability_counter;
    bool is_valid;
} thumbwheel_decade_state_t;

typedef struct {
    const thumbwheel_config_t *config;
    thumbwheel_decade_state_t decades[THUMBWHEEL_MAX_DECADES];
    uint32_t validated_value;
    bool has_error;
} thumbwheel_driver_t;

void thumbwheel_init(thumbwheel_driver_t *driver, const thumbwheel_config_t *config);
