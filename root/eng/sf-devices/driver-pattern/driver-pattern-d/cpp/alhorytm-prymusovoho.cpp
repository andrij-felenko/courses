namespace driver {

struct GpioPinView {
    uint8_t pin;
    void set_mode_od() const noexcept;
    void set_mode_in() const noexcept;
    void write(bool level) const noexcept;
    [[nodiscard]] bool read() const noexcept;
};

inline void recover_i2c_bus(GpioPinView scl, GpioPinView sda) noexcept {
    scl.set_mode_od();
    sda.set_mode_in();

    for (int i = 0; i < 9; ++i) {
        if (sda.read()) {
            break; // Лінію звільнено
        }
        scl.write(false);
        // Затримка 5 мкс
        asm volatile("nop");
        scl.write(true);
        asm volatile("nop");
    }

    sda.set_mode_od();
    sda.write(false);
    scl.write(true);
    sda.write(true);
}

} // namespace driver
