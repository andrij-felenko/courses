/* Фрагмент застарілого board-файлу епохи Linux 2.6 */
static struct i2c_board_info my_i2c_devices[] __initdata = {
    {
        I2C_BOARD_INFO("tmp102", 0x48),
    },
    {
        I2C_BOARD_INFO("pcf85063", 0x51),
        .irq = 42,
    },
};

static struct platform_device my_led_device = {
    .name = "leds-gpio",
    .id = -1,
    .dev = {
        .platform_data = &my_led_data,
    },
};
