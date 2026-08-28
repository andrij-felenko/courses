static i2c_handle_t g_i2c1_handle;
static i2c_handle_t g_i2c2_handle;

void app_init(void) {
    i2c_config_t cfg_fast = { .clock_speed_hz = 400000, .timeout_ms = 20, .sda_pin = 7, .scl_pin = 6 };
    i2c_config_t cfg_std  = { .clock_speed_hz = 100000, .timeout_ms = 50, .sda_pin = 9, .scl_pin = 8 };

    i2c_init(&g_i2c1_handle, (void*)0x40005400, &cfg_fast); /* I2C1 base */
    i2c_init(&g_i2c2_handle, (void*)0x40005800, &cfg_std);  /* I2C2 base */
}
