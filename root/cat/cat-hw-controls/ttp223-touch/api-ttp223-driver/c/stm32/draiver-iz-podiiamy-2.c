static touch_button_t btn;

int main(void) {
    HAL_Init();
    SystemClock_Config();
    tb_begin(&btn, GPIOA, GPIO_PIN_0, GPIO_PIN_SET);   // PA0, активний у 1
    led_init();

    while (1) {
        tb_update(&btn);                // рушій драйвера, кожен прохід

        if (tb_pressed(&btn))  printf("торкнулися\r\n");
        if (tb_released(&btn))          // скільки трималися — для довгого натиску
            printf("відпустили, тримали (мс): %lu\r\n", (unsigned long)tb_held_ms(&btn));
        HAL_GPIO_WritePin(LED_PORT, LED_PIN,          // світло, поки палець тут
                          tb_held(&btn) ? GPIO_PIN_SET : GPIO_PIN_RESET);

        // ... тут може крутитися будь-яка інша робота: драйвер нічого не блокує
    }
}
