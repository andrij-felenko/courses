namespace hardware {

class I2cRecovery {
public:
    static void recover_bus(auto& gpio_scl, auto& gpio_sda, auto& i2c_driver) noexcept {
        gpio_scl.set_open_drain();
        gpio_sda.set_open_drain();
        gpio_scl.write(true);
        gpio_sda.write(true);

        if (!gpio_sda.read()) {
            for (uint8_t i = 0; i < 9; ++i) {
                gpio_scl.write(false);
                delay_us(5);
                gpio_scl.write(true);
                delay_us(5);
                if (gpio_sda.read()) {
                    break;
                }
            }
            // Генерація STOP умови
            gpio_sda.write(false);
            delay_us(5);
            gpio_scl.write(true);
            delay_us(5);
            gpio_sda.write(true);
            delay_us(5);
        }

        i2c_driver.reinit();
    }
};

} // namespace hardware
