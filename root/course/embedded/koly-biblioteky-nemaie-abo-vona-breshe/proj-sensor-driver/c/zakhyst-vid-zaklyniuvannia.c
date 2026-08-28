/* Структура низькорівневих операцій прямого керування ніжками GPIO */
typedef struct {
    void (*set_scl)(bool high);
    void (*set_sda)(bool high);
    bool (*get_sda)(void);
    void (*delay_us)(uint32_t us);
    void (*switch_to_gpio_od)(void);
    void (*switch_to_i2c_hardware)(void);
} i2c_gpio_recovery_pins_t;

sensor_status_t i2c_bus_recover_sda_stuck(const i2c_gpio_recovery_pins_t *pins) {
    if (!pins || !pins->set_scl || !pins->set_sda || !pins->get_sda || !pins->delay_us) {
        return SENSOR_ERR_NULL_PTR;
    }

    /* 1. Перемикаємо виводи в режим GPIO Open-Drain */
    pins->switch_to_gpio_od();
    pins->set_scl(true);
    pins->set_sda(true);
    pins->delay_us(5);

    /* 2. Якщо SDA вже високий, лінія не заблокована */
    if (!pins->get_sda()) {
        /* 3. Генеруємо до 9 тактових імпульсів на SCL для виштовхування бітів із сенсора */
        for (uint8_t i = 0; i < 9; i++) {
            pins->set_scl(false);
            pins->delay_us(5);
            pins->set_scl(true);
            pins->delay_us(5);

            /* Якщо ведений пристрій відпустив SDA, припиняємо тактування */
            if (pins->get_sda()) {
                break;
            }
        }
    }

    /* 4. Перевіряємо, чи відпустив ведений лінію SDA */
    if (!pins->get_sda()) {
        pins->switch_to_i2c_hardware();
        return SENSOR_ERR_BUS_STUCK; /* Фізичне заклинювання або коротке замикання на землю */
    }

    /* 5. Формуємо умову STOP: перепад SDA 0 -> 1 при високому SCL */
    pins->set_sda(false);
    pins->delay_us(5);
    pins->set_scl(true);
    pins->delay_us(5);
    pins->set_sda(true);
    pins->delay_us(5);

    /* 6. Повертаємо виводи під контроль апаратного контролера I2C */
    pins->switch_to_i2c_hardware();
    return SENSOR_OK;
}
