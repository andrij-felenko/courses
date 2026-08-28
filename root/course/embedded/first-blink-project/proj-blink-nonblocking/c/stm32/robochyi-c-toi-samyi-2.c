#define LED_INT     200              // блимати кожні 200 мс
#define SENSOR_INT  1000             // читати давач кожну 1000 мс

int main(void) {
    HAL_Init();
    SystemClock_Config();
    MX_GPIO_Init();

    uint32_t lastBlink = 0, lastSensor = 0;
    bool ledOn = false;

    while (1) {
        uint32_t now = HAL_GetTick();

        // справа 1: блимання світлодіодом
        if (now - lastBlink >= LED_INT) {
            lastBlink = now;
            ledOn = !ledOn;
            HAL_GPIO_WritePin(LED_GPIO_Port, LED_Pin,
                              ledOn ? GPIO_PIN_SET : GPIO_PIN_RESET);
        }

        // справа 2: опитування давача — СВОЯ мітка, СВІЙ інтервал
        if (now - lastSensor >= SENSOR_INT) {
            lastSensor = now;
            float t = read_temperature();
            send_temperature(t);
        }

        // обидві гілки бачать один і той самий `now`;
        // жодна не блокує іншу; while(1) пролітає тисячі разів на секунду
    }
}
