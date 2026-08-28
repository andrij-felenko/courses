/* Старий board file для ARM-платформи */
static struct platform_device my_sensor_device = {
    .name = "acme-sensor",
    .id = -1,
    .dev = {
        .platform_data = &(struct my_sensor_platform_data) {
            .reset_gpio = 42,   /* Жорстко прив'язаний номер */
            .irq_gpio   = 43,
        },
    },
};
