#ifndef SECTION_TIMER_H
#define SECTION_TIMER_H

/*
 * Часовий бюджет критичних секцій.
 *
 * Секція із забороненими перериваннями або обробник, що затягнувся, зривають
 * реакцію на зовнішню подію так само надійно, як брак пам'яті. Лічильник
 * тримає останній, найгірший і середній час та рахує зриви терміну.
 */

#include "budget_types.h"

typedef struct {
    const char *name;
    uint32_t    deadline_us; /* відведений термін */
    uint32_t    last_us;
    uint32_t    worst_us;    /* найгірший випадок за весь час роботи */
    uint64_t    total_us;
    uint32_t    runs;
    uint32_t    overruns;
    uint64_t    started_us;
    bool        active;
} section_timer_t;

bool section_timer_init(section_timer_t *timer, const char *name,
                        uint32_t deadline_us);

void section_timer_begin(section_timer_t *timer);

/* Закриває вимір і повертає тривалість у мікросекундах. */
uint32_t section_timer_end(section_timer_t *timer);

uint32_t section_timer_average_us(const section_timer_t *timer);

/* Запас від найгіршого випадку до терміну; від'ємне значення — термін зірвано. */
int32_t section_timer_margin_us(const section_timer_t *timer);

budget_flags_t section_timer_audit(const section_timer_t *timers, size_t count,
                                   size_t *worst_index);

#endif /* SECTION_TIMER_H */
