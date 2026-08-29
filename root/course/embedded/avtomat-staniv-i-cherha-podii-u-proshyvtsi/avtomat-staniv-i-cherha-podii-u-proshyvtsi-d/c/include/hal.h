#ifndef EVSE_HAL_H
#define EVSE_HAL_H

#include <stdbool.h>
#include <stdint.h>

/*
 * Межа порту. Усе, що залежить від конкретної плати, живе за цим заголовком;
 * решта проєкту звертається до апаратури лише через ці функції. Реалізація
 * для стенда — src/hal_port.c; для справжньої станції її замінюють на драйвери
 * периферії мікроконтролера, не чіпаючи жодного рядка логіки автомата.
 */

typedef enum {
    HAL_LED_GREEN = 0, /* станція готова до роботи */
    HAL_LED_BLUE,      /* триває заряджання */
    HAL_LED_RED,       /* аварія */
    HAL_LED_COUNT
} hal_led_t;

void     hal_init(void);
uint32_t hal_millis(void);

/* Силовий контактор трифазної лінії 400 В / 32 А. */
void hal_relay_set(bool closed);
bool hal_relay_is_closed(void);

/* Лінія Control Pilot: ШІМ 1 кГц, шпаруватість задає дозволений струм. */
void hal_pilot_set_duty(uint8_t duty_percent); /* 100 == постійні +12 В */
void hal_pilot_force_low(void);                /* притиснути лінію до 0 В */

/* Зворотне читання лінії CP синхронно з півперіодами ШІМ. */
int16_t  hal_pilot_read_high_mv(void); /* рівень на додатному півперіоді */
int16_t  hal_pilot_read_low_mv(void);  /* рівень на від'ємному півперіоді */
uint32_t hal_pilot_period_us(void);    /* виміряний період, мкс */

/* Трансформатор нульової послідовності: диференційний струм витоку, мА. */
uint16_t hal_leakage_read_ma(void);

void hal_led_set(hal_led_t led, bool on);
void hal_lock_actuator(bool locked); /* соленоїд замка роз'єму */

/*
 * Критична секція. hal_irq_save() забороняє переривання й повертає попередній
 * стан маски, hal_irq_restore() відновлює саме його — а не вмикає переривання
 * беззастережно, інакше вкладений виклик розкрив би секцію зовнішнього.
 */
uint32_t hal_irq_save(void);
void     hal_irq_restore(uint32_t saved);

/*
 * Засинання ядра до найближчого переривання (інструкція WFI на Cortex-M).
 * Прокидається навіть із забороненими перериваннями: заявка в NVIC знімає
 * ядро зі сну незалежно від PRIMASK — на цьому тримається безпечна перевірка
 * порожньої черги в main().
 */
void hal_wait_for_interrupt(void);

#endif /* EVSE_HAL_H */
