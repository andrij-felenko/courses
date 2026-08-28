// Керування яскравістю світлодіода через апаратний ШІМ ESP32 (LEDC).
// Струм задано драйвером апаратно; ми лише міняємо шпаруватість.
#define LED_EN_PIN   25          // ніжка EN драйвера струму
#define PWM_CH        0
#define PWM_FREQ      20000       // 20 кГц — вище за поріг видимого мерехтіння
#define PWM_BITS      8           // 8-бітна роздільність: 0..255

void led_dim_setup(void) {
    ledcSetup(PWM_CH, PWM_FREQ, PWM_BITS);
    ledcAttachPin(LED_EN_PIN, PWM_CH);
}

// brightness: 0 (темно) .. 255 (повна яскравість).
// Струм у ввімкненій фазі щоразу повний — колір не пливе.
void led_set_brightness(uint8_t brightness) {
    ledcWrite(PWM_CH, brightness);   // шпаруватість = brightness/255
}

void setup() {
    led_dim_setup();
    led_set_brightness(64);          // ~25 % яскравості; світлодіод бере
                                     // повний струм 25 % часу, решту — вимкнений
}
