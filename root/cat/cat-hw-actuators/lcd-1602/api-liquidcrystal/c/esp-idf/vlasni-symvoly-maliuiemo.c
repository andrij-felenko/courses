// той самий масив, лише тип: static const uint8_t degree[8] = { … };
void app_main(void) {
    lcd_init();
    lcd_create_char(0, degree);  // покласти картинку у комірку CGRAM №0

    lcd_set_cursor(0, 0);
    lcd_print("Temp: 23.5");
    lcd_write_char(0);           // вивести символ із комірки №0 → «°»
    lcd_print("C");
}
