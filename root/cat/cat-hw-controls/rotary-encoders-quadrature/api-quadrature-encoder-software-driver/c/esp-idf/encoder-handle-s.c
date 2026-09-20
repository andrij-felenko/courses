#include <stdint.h>
#include <stdbool.h>

typedef enum {
    ENCODER_MODE_1X = 1,
    ENCODER_MODE_2X = 2,
    ENCODER_MODE_4X = 4
} encoder_mode_t;

typedef struct {
    int32_t gpio_phase_a;
    int32_t gpio_phase_b;
    int32_t gpio_button;
    uint32_t ppr;
    encoder_mode_t mode;
    bool invert_direction;
    int32_t min_position;
    int32_t max_position;
    uint32_t button_debounce_ms;
    bool enable_index_pin;
} encoder_config_t;

typedef struct encoder_handle_s* encoder_handle_t;

// Функція ініціалізації драйвера енкодера
int32_t encoder_init(encoder_handle_t *handle, const encoder_config_t *config);
