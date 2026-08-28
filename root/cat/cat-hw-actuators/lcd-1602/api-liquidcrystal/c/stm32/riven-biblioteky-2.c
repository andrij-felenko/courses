int main(void) {
    HAL_Init();
    SystemClock_Config();
    MX_GPIO_Init();        // CubeMX: шість ніжок дисплея як GPIO_Output

    lcd_init();            // свій драйвер (складемо нижче)
    lcd_print("Hello!");   // напис з клітинки (0,0)

    while (1) { }
}
