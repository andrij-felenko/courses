/* Швидкі макроси стробування GPIO на C */
#define PROFILING_PORT       GPIOB
#define PROFILING_PIN_MASK   (1U << 5)

/* Встановлення високого рівня на початку ділянки */
#define PROFILING_PIN_HIGH() do { PROFILING_PORT->BSRR = PROFILING_PIN_MASK; } while(0)

/* Скидання у низький рівень наприкінці ділянки */
#define PROFILING_PIN_LOW()  do { PROFILING_PORT->BSRR = (PROFILING_PIN_MASK << 16); } while(0)

void EXTI0_IRQHandler(void) {
    PROFILING_PIN_HIGH(); // Підйом фронту для осцилографа

    /* Корисна робота обробника */
    process_urgent_sensor_event();

    PROFILING_PIN_LOW();  // Спад фронту
}
