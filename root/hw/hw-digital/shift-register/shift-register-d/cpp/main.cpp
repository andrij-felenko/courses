#define PIN_DATA   2
#define PIN_CLK    3
#define PIN_LATCH  4

// Засунути один байт у зсувний регістр (старший біт першим)
void shift_out_byte(uint8_t value) {
    for (int i = 7; i >= 0; i--) {       // від біта 7 (старший) до 0
        int bit = (value >> i) & 1;      // витягуємо i-й біт
        gpio_write(PIN_DATA, bit);       // 1) виставили дані
        gpio_write(PIN_CLK, 1);          // 2) фронт такту: біт «затік»,
        gpio_write(PIN_CLK, 0);          //    решта зсунулась на щабель
    }
}

// Показати байт на виходах: засунути 8 бітів, тоді клацнути латчем
void show_byte(uint8_t value) {
    shift_out_byte(value);
    gpio_write(PIN_LATCH, 1);            // один імпульс RCLK копіює
    gpio_write(PIN_LATCH, 0);            //    рядок у вихідний латч
}
