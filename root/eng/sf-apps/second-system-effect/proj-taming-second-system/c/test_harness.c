// --- test_harness.c: детерміноване джерело замість давача ---
static const int32_t FAKE[] = { 2510, 2515, 2500, 2530, 2495 };  // сотні °C
static uint8_t fake_pos;

int32_t bmp280_read_centi_celsius(void) {   // підміна на час тесту
    return FAKE[fake_pos++ % 5];
}

int main(void) {
    app_init();                              // реєструє "bmp280"
    for (int i = 0; i < 5; i++) {
        float t = read_temperature();
        print_float("t", t);                 // друкуємо еталон
    }
    return 0;
}
