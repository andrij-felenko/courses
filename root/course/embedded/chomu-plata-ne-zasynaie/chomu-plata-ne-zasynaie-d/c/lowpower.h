/* lowpower.h — детермінований автомат присипляння плати.
 *
 * Порядок кроків тут не косметичний: паркування ліній мусить статися до
 * розмикання ключа, аналоговий режим — після, а WFI — тільки коли озброєне
 * джерело пробудження й аудит не знайшов плаваючих входів.
 */
#ifndef LOWPOWER_H
#define LOWPOWER_H

#include <stdbool.h>
#include <stdint.h>

typedef enum {
    SLEEP_STAGE_AWAKE = 0,
    SLEEP_STAGE_BUSES_PARKED,
    SLEEP_STAGE_RAIL_OFF,
    SLEEP_STAGE_PINS_ANALOG,
    SLEEP_STAGE_DEBUG_SILENT,
    SLEEP_STAGE_WAKE_ARMED,
    SLEEP_STAGE_READY
} sleep_stage_t;

typedef enum {
    SLEEP_OK = 0,
    SLEEP_ERR_SEQUENCE,        /* крок викликано не в тому порядку */
    SLEEP_ERR_RAIL_POWERED,    /* ключ розімкнено, а шина датчика жива */
    SLEEP_ERR_FLOATING_PINS,   /* лишилися цифрові входи без підтяжки */
    SLEEP_ERR_NO_WAKE_SOURCE,  /* нікому розбудити: заснули б назавжди */
    SLEEP_ERR_RTC_TIMEOUT,     /* таймер пробудження не прийняв нове значення */
    SLEEP_ERR_PROBE_ATTACHED   /* попередження: зонд приєднаний, вимір недостовірний */
} sleep_err_t;

/* Причина, з якої ядро прокинулося. */
typedef enum {
    WAKE_RTC = 0,
    WAKE_BUTTON,
    WAKE_UNKNOWN
} wake_source_t;

/* Одноразове налаштування RTC на LSE: тільки таймер пробудження, календар
 * цій задачі не потрібен. */
sleep_err_t lowpower_rtc_init(void);

/* Повний цикл присипляння в Stop2 на задану кількість секунд.
 * Повертає перший діагностований дефект; SLEEP_ERR_PROBE_ATTACHED — м'який,
 * сон усе одно відбудеться. */
sleep_err_t lowpower_enter_stop2(uint32_t seconds);

/* Standby: RAM не зберігається, зате струм у сотні нА. Рівні на виводах
 * задають регістри PWR, а не GPIO. */
sleep_err_t lowpower_enter_standby(uint32_t seconds);

wake_source_t lowpower_last_wake_source(void);
sleep_stage_t lowpower_stage(void);
uint32_t lowpower_floating_mask_b(void);

#endif /* LOWPOWER_H */
