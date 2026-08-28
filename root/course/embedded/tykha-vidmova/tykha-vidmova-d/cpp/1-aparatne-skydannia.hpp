void reset_sensor_hardware(GpioPin power_en, GpioPin sda, GpioPin scl, I2cDriver& i2c) noexcept {
    // 1. Зняти живлення
    power_en.write(PinState::High);

    // 2. Скинути лінії у нуль проти паразитного живлення через ESD-захист
    sda.set_mode(PinMode::Output);
    scl.set_mode(PinMode::Output);
    sda.write(PinState::Low);
    scl.write(PinState::Low);

    // 3. Пауза на розряд ємностей обв'язки
    system_sleep_ms(50);

    // 4. Подати живлення та реініціалізувати шину
    power_en.write(PinState::Low);
    system_sleep_ms(20);
    i2c.reinitialize();
}
