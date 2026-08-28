// SSR несе опторозв'язку всередині: вхід керується логічним рівнем 3.3 В
#define SSR_PIN  4                 // GPIO ESP32 на вхід SSR через резистор

void lamp_init(void) {
    gpio_set_direction(SSR_PIN, GPIO_MODE_OUTPUT);
    gpio_set_level(SSR_PIN, 0);    // мережа вимкнена, доки не накажемо
}

void lamp_on(void)  { gpio_set_level(SSR_PIN, 1); }   // увімкнути навантаження
void lamp_off(void) { gpio_set_level(SSR_PIN, 0); }   // вимкнути
