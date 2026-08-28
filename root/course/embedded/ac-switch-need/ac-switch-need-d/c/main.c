// Опто-драйвер симістора (MOC3021) керується логічним рівнем через резистор.
// GPIO живить лише вхідний світлодіод драйвера; мережа — за оптичним бар'єром.
#define HEATER_PIN  4              // GPIO ESP32 → 120 Ом → світлодіод MOC3021

void heater_init(void) {
    gpio_set_direction(HEATER_PIN, GPIO_MODE_OUTPUT);
    gpio_set_level(HEATER_PIN, 0); // нагрівач вимкнено, доки не накажемо
}

void heater_on(void)  { gpio_set_level(HEATER_PIN, 1); }  // світлодіод світить → симістор проводить
void heater_off(void) { gpio_set_level(HEATER_PIN, 0); }  // світло гасне → симістор гасне на найближчому нулі струму
