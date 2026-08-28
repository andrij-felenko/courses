#include <stdint.h>

// База DPRAM у адресному просторі мікроконтролера (приклад).
#define DPRAM      ((volatile uint8_t *)0x8000)
#define DP_MBOX_R  0x3FF          // скринька, запис у яку будить ПРАВИЙ порт

// Ліве ядро: покласти байт і штовхнути праве ядро перериванням.
void left_send(uint16_t addr, uint8_t value)
{
    DPRAM[addr] = value;         // 1) кладемо дані у спільну комірку
    DPRAM[DP_MBOX_R] = 0;        // 2) пишемо у скриньку правого → у нього спалахує INT
}

// Праве ядро: обробник переривання INT.
void right_on_int(void)
{
    volatile uint8_t ack = DPRAM[DP_MBOX_R];  // читання скриньки ГАСИТЬ мій INT
    (void)ack;
    // ... тут забрати дані зі спільних комірок і обробити ...
}
