#include <stdint.h>
#include <stdbool.h>

/* Приклад низькорівневої реалізації Bus Recovery для мікроконтролера */

typedef struct {
    void (*scl_set_output)(void);
    void (*sda_set_input)(void);
    void (*sda_set_output)(void);
    void (*scl_write)(bool level);
    void (*sda_write)(bool level);
    bool (*sda_read)(void);
    void (*delay_us)(uint32_t us);
    void (*restore_i2c_pins)(void);
} i2c_recovery_gpio_ops_t;

bool i2c_bus_recover(const i2c_recovery_gpio_ops_t *ops) {
    if (!ops) return false;

    /* 1. Налаштовуємо виводи під ручне керування */
    ops->scl_set_output();
    ops->sda_set_input();
    ops->scl_write(true);
    ops->delay_us(10);

    /* 2. Якщо SDA висока — шина вже вільна */
    if (ops->sda_read()) {
        ops->restore_i2c_pins();
        return true;
    }

    /* 3. Генеруємо до 9 тактів SCL, щоб ведений відпустив SDA */
    bool recovered = false;
    for (int i = 0; i < 9; ++i) {
        ops->scl_write(false);
        ops->delay_us(5);
        ops->scl_write(true);
        ops->delay_us(5);

        if (ops->sda_read()) {
            recovered = true;
            break;
        }
    }

    if (!recovered) {
        /* Лінія все ще замкнена на землю — апаратне коротке замикання або мертвий чіп */
        ops->restore_i2c_pins();
        return false;
    }

    /* 4. Формуємо коректну умову STOP через GPIO */
    ops->sda_set_output();
    ops->scl_write(false);
    ops->sda_write(false);
    ops->delay_us(5);

    ops->scl_write(true);
    ops->delay_us(5);
    ops->sda_write(true);
    ops->delay_us(5);

    /* 5. Повертаємо піни апаратному контролеру */
    ops->restore_i2c_pins();
    return true;
}
