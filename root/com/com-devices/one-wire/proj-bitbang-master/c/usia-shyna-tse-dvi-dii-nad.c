#include <avr/io.h>
#include <avr/interrupt.h>
#include <util/delay.h>          // _delay_us — цикл-точні паузи при F_CPU

#define OW_BIT   (1 << PD2)      // жила висить на ніжці PD2 (цифровий 2 на Uno)

// PORTD-біт завжди 0: як вихід ніжка дає нуль; як вхід — просто відпущена (hi-Z).
static inline void    ow_drive_low(void) { DDRD |=  OW_BIT; }  // вихід-0 → притиснули
static inline void    ow_release(void)   { DDRD &= ~OW_BIT; }  // вхід-Z  → відпустили
static inline uint8_t ow_sample(void)    { return (PIND & OW_BIT) ? 1 : 0; }

void ow_init(void) {
    PORTD &= ~OW_BIT;   // ніколи не подаємо «1»: біт даних лишається 0
    DDRD  &= ~OW_BIT;   // старт як вхід — лінія відпущена, її тримає підтяжка Rp
}
