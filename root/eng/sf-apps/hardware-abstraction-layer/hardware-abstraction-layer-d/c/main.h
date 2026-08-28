/* Загальний інтерфейс лінії GPIO */
struct hal_gpio_pin;

typedef struct {
    hal_status_t (*set_level)(const struct hal_gpio_pin *pin, hal_gpio_level_t level);
    hal_status_t (*get_level)(const struct hal_gpio_pin *pin, hal_gpio_level_t *out_level);
    hal_status_t (*toggle)(const struct hal_gpio_pin *pin);
} hal_gpio_ops_t;

typedef struct hal_gpio_pin {
    const hal_gpio_ops_t *ops;
    void *ctx;
} hal_gpio_pin_t;
