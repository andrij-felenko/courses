void lcd_init(void) {
    // 0. Ніжки на вихід: у CubeMX усі шість позначені GPIO_Output —
    //    тут лишається завести E в нуль перед першим стробом.
    HAL_GPIO_WritePin(LCD_E_PORT, LCD_E_PIN, GPIO_PIN_RESET);

    HAL_Delay(50);           // 1. Живлення встоялося: чекаємо ≥ 40 мс після подачі

    // 2. Тричі напівбайт 0011 — надійно завести у 8-бітний режим із будь-якого стану.
    //    Це ще НЕ повні байти: шлемо самі напівбайти, стробом кожен.
    HAL_GPIO_WritePin(LCD_RS_PORT, LCD_RS_PIN, GPIO_PIN_RESET);
    put_nibble(0x03); pulse_e(); HAL_Delay(5);    // перший раз: пауза > 4.1 мс
    put_nibble(0x03); pulse_e(); delay_us(150);   // другий: > 100 мкс
    put_nibble(0x03); pulse_e(); delay_us(150);   // третій

    // 3. Тепер напівбайт 0010 — перемкнути у 4-бітний режим.
    put_nibble(0x02); pulse_e(); delay_us(150);

    // 4. Звідси — вже ПОВНІ байти (send_byte ріже їх на два напівбайти).
    lcd_command(0x28);       // Function Set: 4 біти, 2 рядки, шрифт 5×8
    lcd_command(0x08);       // Display OFF
    lcd_command(0x01); HAL_Delay(2);   // Clear Display (довга — пауза ~1.52 мс)
    lcd_command(0x06);       // Entry Mode: курсор вправо, без зсуву екрана
    lcd_command(0x0C);       // Display ON, курсор і блимання вимкнені
}
