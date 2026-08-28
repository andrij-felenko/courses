volatile uint32_t turns = 0;           // спільне з ISR → volatile

/* ніжка налаштована як GPIO_MODE_IT_RISING, її лінія EXTI ввімкнена в NVIC;
   HAL сам кличе цей callback із обробника переривання */
void HAL_GPIO_EXTI_Callback(uint16_t pin) {      // ISR: коротка, лише ++
    if (pin == SENSOR_Pin)
        turns++;
}

int main(void) {
    HAL_Init();
    MX_GPIO_Init();

    while (1) {
        // ... вільний для решти роботи; залізо рахує саме ...
    }
}
