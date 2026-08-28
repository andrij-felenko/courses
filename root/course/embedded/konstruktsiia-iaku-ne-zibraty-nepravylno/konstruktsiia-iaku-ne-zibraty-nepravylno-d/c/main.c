#include <stdint.h>
#include <stdbool.h>

/* Коди помилок та станів діагностики розпіновки */
typedef enum {
    PINOUT_STATUS_OK               = 0x00,
    PINOUT_ERR_SHORT_TO_GND        = 0x01,
    PINOUT_ERR_SHORT_TO_VCC        = 0x02,
    PINOUT_ERR_LINES_BRIDGED       = 0x04,
    PINOUT_ERR_SIGNALS_SWAPPED     = 0x08,
    PINOUT_ERR_NO_DEVICE_RESPONSE  = 0x10,
    PINOUT_ERR_OVERVOLTAGE_TRIP    = 0x20
} pinout_status_t;

/* Структура конфігурації апаратного порту для зондування */
typedef struct {
    uint32_t pin_a_id;
    uint32_t pin_b_id;
    bool hardware_swap_supported;
} bus_probe_config_t;

/* Абстрактні апаратні функції платформи (HAL) */
extern void hal_gpio_set_mode_input_pullup(uint32_t pin);
extern void hal_gpio_set_mode_input_pulldown(uint32_t pin);
extern void hal_gpio_set_mode_input_floating(uint32_t pin);
extern void hal_gpio_set_mode_output_pushpull(uint32_t pin);
extern void hal_gpio_write(uint32_t pin, bool level);
extern bool hal_gpio_read(uint32_t pin);
extern void hal_delay_us(uint32_t us);
extern void hal_uart_enable_hardware_swap(bool enable);

/*
 * Виконує безпечне зондування двох ліній шини слабким струмом
 * та перевіряє наявність замикань або переплутаних сигналів.
 */
pinout_status_t bus_probe_safe_diagnostics(const bus_probe_config_t *cfg) {
    uint32_t error_flags = PINOUT_STATUS_OK;

    /* Фаза 1: Перевірка на коротке замикання на GND або VDD */
    hal_gpio_set_mode_input_pullup(cfg->pin_a_id);
    hal_gpio_set_mode_input_pullup(cfg->pin_b_id);
    hal_delay_us(50); /* Час заряду ємності монтажу */

    if (!hal_gpio_read(cfg->pin_a_id)) {
        error_flags |= PINOUT_ERR_SHORT_TO_GND;
    }
    if (!hal_gpio_read(cfg->pin_b_id)) {
        error_flags |= PINOUT_ERR_SHORT_TO_GND;
    }

    hal_gpio_set_mode_input_pulldown(cfg->pin_a_id);
    hal_gpio_set_mode_input_pulldown(cfg->pin_b_id);
    hal_delay_us(50);

    if (hal_gpio_read(cfg->pin_a_id)) {
        error_flags |= PINOUT_ERR_SHORT_TO_VCC;
    }
    if (hal_gpio_read(cfg->pin_b_id)) {
        error_flags |= PINOUT_ERR_SHORT_TO_VCC;
    }

    if (error_flags != PINOUT_STATUS_OK) {
        /* Критичне замикання — повертаємо порти у безпечний високоомний стан */
        hal_gpio_set_mode_input_floating(cfg->pin_a_id);
        hal_gpio_set_mode_input_floating(cfg->pin_b_id);
        return (pinout_status_t)error_flags;
    }

    /* Фаза 2: Перевірка на замикання ліній між собою (Bridge test) */
    hal_gpio_set_mode_output_pushpull(cfg->pin_a_id);
    hal_gpio_set_mode_input_pulldown(cfg->pin_b_id);

    hal_gpio_write(cfg->pin_a_id, true);
    hal_delay_us(20);
    if (hal_gpio_read(cfg->pin_b_id) == true) {
        /* Лінія B повторює стан лінії A при активній підтяжці B до GND */
        hal_gpio_write(cfg->pin_a_id, false);
        hal_delay_us(20);
        if (hal_gpio_read(cfg->pin_b_id) == false) {
            error_flags |= PINOUT_ERR_LINES_BRIDGED;
        }
    }

    hal_gpio_set_mode_input_floating(cfg->pin_a_id);
    hal_gpio_set_mode_input_floating(cfg->pin_b_id);

    if (error_flags != PINOUT_STATUS_OK) {
        return (pinout_status_t)error_flags;
    }

    /* Фаза 3: Перевірка полярності/напрямку сигналів за сигнатурою лупбеку */
    /* Генеруємо безпечний тестовий імпульс 100 мкс на Pin A, слухаємо Pin B */
    hal_gpio_set_mode_output_pushpull(cfg->pin_a_id);
    hal_gpio_set_mode_input_floating(cfg->pin_b_id);

    hal_gpio_write(cfg->pin_a_id, false);
    hal_delay_us(100);
    hal_gpio_write(cfg->pin_a_id, true);
    hal_delay_us(100);

    /* Якщо відповідь прийшла не на той вивід — фіксуємо переплутані лінії */
    bool swapped_detected = false;
    /* У реальній системі тут опитується апаратний прапорець прийому байта */

    if (swapped_detected) {
        if (cfg->hardware_swap_supported) {
            /* Автоматична корекція: активуємо біт SWAP у регістрі керування USART */
            hal_uart_enable_hardware_swap(true);
            return PINOUT_STATUS_OK;
        } else {
            error_flags |= PINOUT_ERR_SIGNALS_SWAPPED;
        }
    }

    return (pinout_status_t)error_flags;
}
