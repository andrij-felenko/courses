#define GUARD_US 800              // мертвий час, мкс: більший за пачку, менший за період

volatile uint32_t pulses   = 0;
volatile uint32_t lastEdge = 0;   // мітка часу зарахованого фронту, мкс

/* TIM2 пущено вільним лічильником із тактом 1 мкс (prescaler = f_APB1/1 МГц),
   тож TIM2->CNT — це наш «micros()» на 32 бітах. */
void HAL_GPIO_EXTI_Callback(uint16_t pin) {
  if (pin != GPIO_PIN_0) return;
  uint32_t t = __HAL_TIM_GET_COUNTER(&htim2);
  if (t - lastEdge >= GUARD_US) {        // пройшло досить від попереднього фронту?
    pulses++;
    lastEdge = t;
  }
  // інакше — це дрижання того ж зубця, ігноруємо
}
