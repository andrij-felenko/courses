#include <stdint.h>

// Чотири виводи, на яких висять резистори R, R/2, R/4, R/8.
// PIN_B0 — наймолодший біт (через найбільший резистор R),
// PIN_B3 — старший біт (через найменший резистор R/8).
#define PIN_B0  0   // вага 1
#define PIN_B1  1   // вага 2
#define PIN_B2  2   // вага 4
#define PIN_B3  3   // вага 8

// Виставити 4-бітне значення на ЦАП із зважених резисторів.
void dac_write(uint8_t value)
{
    gpio_write(PIN_B0, (value >> 0) & 1);   // наймолодший біт
    gpio_write(PIN_B1, (value >> 1) & 1);
    gpio_write(PIN_B2, (value >> 2) & 1);
    gpio_write(PIN_B3, (value >> 3) & 1);   // старший біт
}

int main(void)
{
    dac_write(11);   // 1011 → очікуємо рівень коду 11 із 15
    for (;;) { }
}
