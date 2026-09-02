/* Шар доступу до заліза плати: один світлодіод активного нуля на PC13 і одна
   тактова кнопка на PA0 із зовнішнім RC-фільтром (R1=10 кОм, R2=100 Ом, C=100 нФ). */
#ifndef BOARD_H
#define BOARD_H

#include <stdbool.h>
#include <stdint.h>

/* Після скидання ядро тактує внутрішній генератор HSI: 8 МГц. PLL не вмикаємо —
   для кнопки й світлодіода зайвого такту не треба, а код лишається коротким. */
#define F_CPU 8000000UL

void board_init(void);

/* Сирий рівень на ніжці кнопки: 1 — відпущена (тримає підтяжка), 0 — натиснута. */
uint8_t board_button_level(void);

void board_led_set(bool on);
void board_led_toggle(void);
bool board_led_is_on(void);

/* Вмикає переривання SysTick із періодом 10 мс — база періодичного опитування. */
void board_systick_start_10ms(void);

#endif /* BOARD_H */
