namespace Health {

struct I2CDriverOps {
    std::function<void()>     set_scl_mode_gpio{};
    std::function<void()>     set_scl_mode_alternate{};
    std::function<void(bool)> set_scl_pin{};
    std::function<void(bool)> set_sda_pin{};
    std::function<bool()>     read_scl_pin{};
    std::function<bool()>     read_sda_pin{};
    std::function<void(uint32_t)> delay_us{};
    std::function<void()>     reset_i2c_peripheral{};
};

[[nodiscard]] bool recover_i2c_bus(const I2CDriverOps& ops) noexcept {
    if (!ops.set_scl_mode_gpio || !ops.set_scl_pin || !ops.read_sda_pin) {
        return false;
    }

    if (ops.read_sda_pin() && ops.read_scl_pin()) {
        return true;
    }

    ops.set_scl_mode_gpio();
    ops.set_scl_pin(true);
    ops.set_sda_pin(true);
    ops.delay_us(10);

    for (int i = 0; i < 9; ++i) {
        ops.set_scl_pin(false);
        ops.delay_us(10);
        ops.set_scl_pin(true);
        ops.delay_us(10);

        if (ops.read_sda_pin()) {
            break;
        }
    }

    ops.set_sda_pin(false);
    ops.delay_us(10);
    ops.set_scl_pin(true);
    ops.delay_us(10);
    ops.set_sda_pin(true);
    ops.delay_us(10);

    ops.set_scl_mode_alternate();
    ops.reset_i2c_peripheral();

    return (ops.read_sda_pin() && ops.read_scl_pin());
}

} // namespace Health
