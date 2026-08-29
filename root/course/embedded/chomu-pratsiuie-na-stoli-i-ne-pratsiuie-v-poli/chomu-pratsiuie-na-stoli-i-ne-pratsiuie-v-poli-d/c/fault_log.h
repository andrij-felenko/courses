/* fault_log.h — причина перезапуску й журнал аварій у резервному домені RTC.
 *
 * Двадцять слів, які переживають скидання й короткий провал живлення, —
 * уся пам'ять, що лишається після Brownout-перезапуску. Тому вони розписані
 * до біта, а не «якось». Перше, що робить польовий прилад після старту, —
 * з'ясовує, ЧОМУ він стартував: без цього нескінченний цикл перезавантажень
 * ззовні виглядає як нормальна робота.
 */
#ifndef FAULT_LOG_H
#define FAULT_LOG_H

#include <stdbool.h>
#include <stdint.h>

typedef enum {
    RESET_CAUSE_UNKNOWN = 0,
    RESET_CAUSE_POWER_ON,   /* штатне ввімкнення */
    RESET_CAUSE_PIN,        /* зовнішня кнопка NRST */
    RESET_CAUSE_BROWNOUT,   /* просадка шини нижче порогу BOR */
    RESET_CAUSE_WATCHDOG,   /* зависання: сторожовий таймер не нагодували */
    RESET_CAUSE_HARD_FAULT, /* виняток процесора, зафіксований обробником */
    RESET_CAUSE_SOFTWARE,   /* навмисний перезапуск із коду */
    RESET_CAUSE_LOW_POWER   /* збій виходу з режиму зниженого споживання */
} reset_cause_t;

#define FAULT_LOG_SLOTS 16u

typedef struct {
    reset_cause_t cause;
    int16_t temperature_c; /* округлено до градуса, −64…+191 */
    uint16_t voltage_mv;   /* крок 16 мВ */
    uint16_t uptime_s;     /* скільки прожив до аварії, стеля 8191 с */
} fault_event_t;

typedef struct {
    uint16_t boots;
    uint16_t brownouts;
    uint16_t watchdogs;
    uint16_t bus_recoveries;
} fault_counters_t;

typedef struct {
    reset_cause_t cause;
    bool history_lost; /* домен був порожній: попередню історію втрачено */
    uint32_t fault_pc; /* молодші 24 біти адреси, де впав HardFault */
    fault_counters_t counters;
} boot_report_t;

/* Читає прапори заліза, розмічає домен за потреби, оновлює лічильники
 * й повертає підсумок. Викликати один раз, на самому початку main(). */
void fault_log_open(boot_report_t *report);

void fault_log_append(reset_cause_t cause, int16_t temperature_c, uint16_t voltage_mv,
                      uint32_t uptime_ms);

/* Читає до max подій від найсвіжішої до найстарішої. Повертає скільки віддав. */
uint8_t fault_log_read(fault_event_t *out, uint8_t max);

void fault_log_bump_recovery(void);

const char *fault_log_cause_name(reset_cause_t cause);

/* Чи входити після такого старту одразу в обережний режим: серія Brownout
 * або сторожових скидань означає, що залізо ще не в нормі. */
bool fault_log_needs_safe_start(const boot_report_t *report);

#endif /* FAULT_LOG_H */
