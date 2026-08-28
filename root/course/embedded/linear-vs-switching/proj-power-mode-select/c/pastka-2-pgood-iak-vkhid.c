static void power_gpio_init(void)
{
    for (size_t i = 0; i < RAIL_COUNT; i++) {
        // EN — вихід, стартово 0 (усе вимкнено, поки не наказали інакше).
        gpio_set_direction(RAILS[i].en_pin, GPIO_MODE_OUTPUT);
        gpio_set_level(RAILS[i].en_pin, 0);

        // PGOOD — вхід із підтяжкою вгору (open-drain на боці перетворювача).
        if (RAILS[i].pgood_pin != GPIO_NUM_NC) {
            gpio_set_direction(RAILS[i].pgood_pin, GPIO_MODE_INPUT);
            gpio_set_pull_mode(RAILS[i].pgood_pin, GPIO_PULLUP_ONLY);
        }
    }
    gpio_set_direction(BUCK_MODE_PIN, GPIO_MODE_OUTPUT);
    gpio_set_direction(MCU_LDO_EN, GPIO_MODE_OUTPUT);
    gpio_set_level(MCU_LDO_EN, 1);   // на старті MCU тримаємо й на LDO — про це нижче
}
