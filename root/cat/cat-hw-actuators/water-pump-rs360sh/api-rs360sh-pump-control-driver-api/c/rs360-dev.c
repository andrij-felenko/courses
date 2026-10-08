#include <stdint.h>
#include <stdbool.h>

// Коди помилок виконання операцій драйвера
typedef enum {
    RS360_OK = 0,
    RS360_ERR_INVALID_ARG,
    RS360_ERR_INIT_FAILED,
    RS360_ERR_DRY_RUN,
    RS360_ERR_OVERCURRENT,
    RS360_ERR_TIMEOUT
} rs360_error_t;

// Структура конфігурації апаратних ресурсів та параметрів драйвера
typedef struct {
    uint32_t pwm_freq_hz;         // Частота ШІМ таймера (оптимально 15000-25000 Гц)
    uint8_t  pwm_gpio_pin;        // Номер піна виходу ШІМ для силового ключа
    uint8_t  dir_gpio_pin;        // Номер піна напрямку (0, якщо однонапрямковий ключ)
    uint8_t  dry_run_gpio_pin;    // Пін дискретного датчика наявності рідини
    uint8_t  adc_current_channel; // Канал АЦП для моніторингу струму
    uint16_t soft_start_ms;       // Тривалість плавного пуску, мс
    uint16_t dry_run_timeout_ms;  // Таймаут спрацьовування захисту від сухого ходу, мс
    float    max_current_amps;    // Поріг струму заклинювання ротора, А
    float    min_current_amps;    // Мінімальний робочий струм (нижче — сухий хід), А
} rs360_config_t;

// Внутрішня структура стану пристрою (прихована за вказівником)
typedef struct rs360_dev rs360_dev_t;
typedef rs360_dev_t* rs360_handle_t;

// Прототип функції ініціалізації драйвера
rs360_error_t rs360_init(const rs360_config_t *config, rs360_handle_t *out_handle);
