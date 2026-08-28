#define PIN_DATA  2
#define PIN_CLK   3

// Засунути байт у тактований регістр, старший біт першим.
// Ключ — порядок: спершу СТАВИМО дані, ПОТІМ робимо фронт.
void clock_in_byte(uint8_t value) {
    for (int i = 7; i >= 0; i--) {
        gpio_write(PIN_DATA, (value >> i) & 1); // 1) виставили біт на DATA
        gpio_write(PIN_CLK, 1);                 // 2) фронт ↑ — комірка ловить біт,
        gpio_write(PIN_CLK, 0);                 //    решта зсувається на щабель
    }
}
