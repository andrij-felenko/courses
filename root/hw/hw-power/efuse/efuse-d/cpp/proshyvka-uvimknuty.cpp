#define EFUSE_EN   GPIO_NUM_25   // керує ніжкою EN мікросхеми eFuse
#define EFUSE_FLT  GPIO_NUM_26   // вхід аварії, активний нуль (open-drain)

void efuse_init(void) {
    gpio_set_direction(EFUSE_EN,  GPIO_MODE_OUTPUT);
    gpio_set_direction(EFUSE_FLT, GPIO_MODE_INPUT);   // назовні підтягнуто до +
    gpio_set_level(EFUSE_EN, 1);                      // відчинити ключ — подати живлення
}

// true, якщо eFuse ЗАРАЗ сигналить про аварію (FLT == 0)
bool efuse_fault(void) {
    return gpio_get_level(EFUSE_FLT) == 0;
}
