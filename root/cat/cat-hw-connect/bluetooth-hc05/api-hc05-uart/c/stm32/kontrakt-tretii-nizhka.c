// CubeMX: STATE → PB5, GPIO_Input із підтяжкою вниз.
// Викликати з головного циклу; printf заведений на huart2.
void state_poll(void) {
    static bool was = false;
    bool now = (HAL_GPIO_ReadPin(GPIOB, GPIO_PIN_5) == GPIO_PIN_SET);

    if (!was && now) printf("З'єднання встановлено.\n");   // 0→1
    if (was && !now) printf("Зв'язок втрачено.\n");        // 1→0
    was = now;

    // Той самий перехід можна ловити не опитуванням, а лінією EXTI на PB5:
    // тоді реакція йде з HAL_GPIO_EXTI_Callback(), а цикл лишається вільним.
}
