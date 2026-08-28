#include <stdint.h>
#include <stdbool.h>

/* --- таблиці й функції put_segments/digit_on/all_digits_off — з кроків 1..3 --- */

volatile uint8_t frame[4] = { 0, 0, 0, 0 };
volatile uint8_t dots      = 0;
static   uint8_t cur       = 0;

void refresh_isr(void)                 // ← причеплено до таймера на 400 Гц
{
    all_digits_off();
    uint8_t seg = frame[cur];
    if (dots & (1u << cur)) seg |= (1u << 7);
    put_segments(seg);
    digit_on(cur);
    cur = (cur + 1) & 3;
}

void show_number(uint16_t value);      // ← з кроку 6

int main(void)
{
    segments_init();      // всі 8 сегментних ніг і 4 катодні — на вихід (нижче)
    timer_init_400hz();   // налаштувати таймер: 400 переривань/с → refresh_isr()
    enable_interrupts();

    uint16_t counter = 0;
    for (;;) {
        show_number(counter);      // оновили те, ЩО показувати
        counter = (counter + 1) % 10000;
        delay_ms(200);             // головний код вільний; розгортка йде сама
        // Поки ми спимо в delay, таймер 80 разів викликав refresh_isr
        // і рівно тримав на екрані поточне число — без нашої участі.
    }
}
