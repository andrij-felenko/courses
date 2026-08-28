/**
 * @brief Процедура апаратного розблокування завислої шини I2C (9 SCL Pulses).
 */
bus_status_t i2c_bus_recover_stuck_sda(void (*set_scl)(bool), void (*set_sda)(bool), bool (*get_sda)(void), void (*delay_us)(uint32_t)) {
    if (!set_scl || !set_sda || !get_sda || !delay_us) return BUS_ERR_INVALID_ARG;

    set_sda(true); // Відпускаємо SDA (Open-Drain підтягнутий до VDD)
    set_scl(true); // Відпускаємо SCL
    delay_us(10);

    // Якщо SDA вже у високому рівні, шина здорова
    if (get_sda()) {
        return BUS_OK;
    }

    // Генеруємо до 9 імпульсів тактування SCL
    for (int i = 0; i < 9; i++) {
        set_scl(false);
        delay_us(10);
        set_scl(true);
        delay_us(10);

        if (get_sda()) {
            break; // Ведений пристрій звільнив лінію SDA
        }
    }

    // Формуємо явний сигнал STOP: при SCL=HIGH переводимо SDA з LOW у HIGH
    set_sda(false);
    delay_us(10);
    set_scl(true);
    delay_us(10);
    set_sda(true);
    delay_us(10);

    return get_sda() ? BUS_OK : BUS_ERR_IO;
}
