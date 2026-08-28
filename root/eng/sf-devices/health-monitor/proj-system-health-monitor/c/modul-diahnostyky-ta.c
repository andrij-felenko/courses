typedef struct {
    void (*set_scl_mode_gpio)(void);
    void (*set_scl_mode_alternate)(void);
    void (*set_scl_pin)(bool high);
    void (*set_sda_pin)(bool high);
    bool (*read_scl_pin)(void);
    bool (*read_sda_pin)(void);
    void (*delay_us)(uint32_t us);
    void (*reset_i2c_peripheral)(void);
} health_i2c_driver_ops_t;

bool health_i2c_recover_bus(const health_i2c_driver_ops_t *ops) {
    if (!ops || !ops->set_scl_mode_gpio || !ops->set_scl_pin || !ops->read_sda_pin) {
        return false;
    }

    // Якщо SDA у високому рівні — шина вільна
    if (ops->read_sda_pin() && ops->read_scl_pin()) {
        return true;
    }

    // 1. Перехід у режим ручного керування GPIO Open-Drain
    ops->set_scl_mode_gpio();
    ops->set_scl_pin(true);
    ops->set_sda_pin(true);
    ops->delay_us(10);

    // 2. Генерація 9 тактових імпульсів на SCL для виштовхування бітів з Slave
    for (int i = 0; i < 9; ++i) {
        ops->set_scl_pin(false);
        ops->delay_us(10);
        ops->set_scl_pin(true);
        ops->delay_us(10);

        // Перевірка: якщо Slave відпустив SDA, можна завершувати
        if (ops->read_sda_pin()) {
            break;
        }
    }

    // 3. Формування умови STOP (SDA: Low -> High при SCL: High)
    ops->set_sda_pin(false);
    ops->delay_us(10);
    ops->set_scl_pin(true);
    ops->delay_us(10);
    ops->set_sda_pin(true);
    ops->delay_us(10);

    // 4. Повернення в штатний режим
    ops->set_scl_mode_alternate();
    ops->reset_i2c_peripheral();

    // Фінальна перевірка стану ліній
    return (ops->read_sda_pin() && ops->read_scl_pin());
}
