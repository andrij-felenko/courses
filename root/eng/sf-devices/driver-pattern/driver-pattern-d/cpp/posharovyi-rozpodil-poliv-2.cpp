namespace {
    driver::I2cDriver g_i2c1{0x40005400, {.clock_speed_hz = 400'000, .timeout_ms = 20, .sda_pin = 7, .scl_pin = 6}};
    driver::I2cDriver g_i2c2{0x40005800, {.clock_speed_hz = 100'000, .timeout_ms = 50, .sda_pin = 9, .scl_pin = 8}};
}

void app_init() {
    auto res1 = g_i2c1.init();
    auto res2 = g_i2c2.init();
    (void)res1;
    (void)res2;
}
