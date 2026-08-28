#define DEBOUNCE_US 1000             // менший за найкоротший реальний період оберту

extern TIM_HandleTypeDef htim2;      // вільно біжить, такт = 1 мкс

volatile uint32_t pulses   = 0;
volatile uint32_t lastEdge = 0;

void HAL_GPIO_EXTI_Callback(uint16_t pin) {
    if (pin != HALL_Pin) return;
    uint32_t now = __HAL_TIM_GET_COUNTER(&htim2);
    if (now - lastEdge < DEBOUNCE_US) return;  // надто рано → тремтіння, ігноруємо
    lastEdge = now;
    pulses++;
}
