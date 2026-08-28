// Переведення SCL у високий рівень з таймаутом у C++
template <typename Gpio, typename Timer>
bool i2c_soft_scl_release_and_wait(Gpio& scl_pin, Timer& timer, uint32_t timeout_us) {
    scl_pin.set_high_z();
    const uint32_t start = timer.get_micros();

    while (!scl_pin.read()) {
        if ((timer.get_micros() - start) >= timeout_us) {
            return false; // Таймаут шини
        }
    }
    return true;
}
