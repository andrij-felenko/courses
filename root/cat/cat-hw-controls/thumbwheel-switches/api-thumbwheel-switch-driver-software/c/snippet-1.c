typedef struct {
    uint8_t pin_pl;       // Пін завантаження паралельних даних (Parallel Load)
    uint8_t pin_clk;      // Пін тактування зсуву (Clock)
    uint8_t pin_data;     // Пін послідовних даних (Serial Data Q7)
    uint8_t num_decades;  // Кількість 4-бітових BCD-декад (від 1 до 8)
    uint32_t debounce_ms; // Час фільтрації брязкоту в мілісекундах
} thumbwheel_config_t;

typedef enum {
    THUMBWHEEL_OK = 0,
    THUMBWHEEL_ERR_INVALID_CONFIG,
    THUMBWHEEL_ERR_INVALID_BCD,
    THUMBWHEEL_ERR_TRANSIENT
} thumbwheel_err_t;

thumbwheel_err_t thumbwheel_init(thumbwheel_t *dev, const thumbwheel_config_t *cfg);
