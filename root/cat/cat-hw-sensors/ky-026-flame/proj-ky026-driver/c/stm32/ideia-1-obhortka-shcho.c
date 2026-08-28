/* DO на PA2, AO на PA0 (ADC1_IN0); обидва виводи звів CubeMX. */
extern ADC_HandleTypeDef hadc1;

static ky026_t sensor = {
    .port_do = GPIOA, .pin_do = GPIO_PIN_2, .hadc = &hadc1,
    .inverted = true, .debounce_ms = 40,
};

int main(void) {
    HAL_Init();
    SystemClock_Config();
    MX_GPIO_Init();                        /* PA2 — вхід DO */
    MX_ADC1_Init();                        /* PA0 — аналоговий AO */
    ky026_begin(&sensor);

    while (1) {
        bool flame = ky026_update(&sensor); /* стабільний стан, без дрижання */
        int  ir    = ky026_strength(&sensor);
        printf("%s  %d\r\n", flame ? "ВОГОНЬ" : "спокій", ir);  /* через UART */
        HAL_Delay(10);                     /* update() любить часті виклики */
    }
}
