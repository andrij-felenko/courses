#include <stdint.h>
#include <stdbool.h>

typedef enum {
    ROTARY_DIP_TYPE_BCD_DIRECT = 0,
    ROTARY_DIP_TYPE_BCD_COMPLEMENTARY,
    ROTARY_DIP_TYPE_HEX_DIRECT,
    ROTARY_DIP_TYPE_HEX_COMPLEMENTARY,
    ROTARY_DIP_TYPE_GRAY_CODE
} rotary_dip_type_t;

typedef struct {
    int32_t gpio_pins[4]; // Виводи розрядів 1, 2, 4, 8
    rotary_dip_type_t type;
    bool active_low;
    uint32_t debounce_ms;
} rotary_dip_config_t;

typedef struct rotary_dip_s* rotary_dip_handle_t;

// Функція декодування сирого коду Ґрея у двійкове число
static inline uint8_t gray_to_binary(uint8_t gray) {
    uint8_t mask = gray >> 1;
    while (mask != 0) {
        gray ^= mask;
        mask >>= 1;
    }
    return gray;
}

int32_t rotary_dip_init(rotary_dip_handle_t *handle, const rotary_dip_config_t *config);
