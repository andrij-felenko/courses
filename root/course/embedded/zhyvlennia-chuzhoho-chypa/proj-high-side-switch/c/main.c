#include <stdint.h>
#include <stdbool.h>

/* Абстракція платформно-залежних викликів GPIO */
extern void hal_gpio_write(uint32_t pin, bool level);
extern void hal_gpio_set_mode_output(uint32_t pin);
extern void hal_gpio_set_mode_input_floating(uint32_t pin);
extern void hal_gpio_set_mode_periph(uint32_t pin);
extern void hal_delay_ms(uint32_t ms);
extern bool hal_i2c_probe_device(uint8_t address);

typedef struct {
    uint32_t pwr_en_pin;
    uint32_t sda_pin;
    uint32_t scl_pin;
    uint8_t  device_i2c_addr;
    uint32_t startup_delay_ms;
    uint32_t discharge_delay_ms;
} PowerDomainConfig;

typedef enum {
    POWER_DOMAIN_OK = 0,
    POWER_DOMAIN_ERR_PROBE_FAILED,
    POWER_DOMAIN_ERR_INVALID_PARAM
} PowerDomainResult;

void power_domain_init(const PowerDomainConfig *cfg) {
    if (!cfg) return;

    /* Початковий безпечний стан: ключ закрито, шини ізольовано */
    hal_gpio_set_mode_output(cfg->pwr_en_pin);
    hal_gpio_write(cfg->pwr_en_pin, false);

    hal_gpio_set_mode_input_floating(cfg->sda_pin);
    hal_gpio_set_mode_input_floating(cfg->scl_pin);
}

PowerDomainResult power_domain_enable(const PowerDomainConfig *cfg) {
    if (!cfg) return POWER_DOMAIN_ERR_INVALID_PARAM;

    /* Крок 1: Відкриваємо High-Side ключ */
    hal_gpio_write(cfg->pwr_en_pin, true);

    /* Крок 2: Чекаємо заряджання ємностей та ініціалізацію POR чипа */
    hal_delay_ms(cfg->startup_delay_ms);

    /* Крок 3: Переводимо піни МК у робочий режим периферійної шини */
    hal_gpio_set_mode_periph(cfg->sda_pin);
    hal_gpio_set_mode_periph(cfg->scl_pin);

    /* Крок 4: Перевіряємо відповідь мікросхеми на шині */
    if (!hal_i2c_probe_device(cfg->device_i2c_addr)) {
        /* Якщо пристрій не відповів, вимикаємо живлення для безпеки */
        hal_gpio_set_mode_input_floating(cfg->sda_pin);
        hal_gpio_set_mode_input_floating(cfg->scl_pin);
        hal_gpio_write(cfg->pwr_en_pin, false);
        return POWER_DOMAIN_ERR_PROBE_FAILED;
    }

    return POWER_DOMAIN_OK;
}

void power_domain_disable(const PowerDomainConfig *cfg) {
    if (!cfg) return;

    /* Крок 1: ІЗОЛЯЦІЯ ШИН перед вимкненням живлення.
       Переводимо піни в High-Z, щоб усунути паразитно відкриті ESD-діоди. */
    hal_gpio_set_mode_input_floating(cfg->sda_pin);
    hal_gpio_set_mode_input_floating(cfg->scl_pin);

    /* Крок 2: Розмикаємо High-Side ключ */
    hal_gpio_write(cfg->pwr_en_pin, false);

    /* Крок 3: Витримуємо час для повного розряду вихідних конденсаторів */
    hal_delay_ms(cfg->discharge_delay_ms);
}
