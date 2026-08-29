#ifndef EVSE_SOFT_TIMER_H
#define EVSE_SOFT_TIMER_H

#include <stdbool.h>
#include <stdint.h>

/*
 * Програмні одноразові таймери — заміна delay(). Автомат «чекає» не спалюючи
 * такти в лічильному циклі, а зводячи таймер: коли термін спливе, тік системи
 * покладе в чергу EVT_TIMEOUT із номером таймера в param.
 */
typedef enum {
    TMR_AUTH_WINDOW = 0,   /* вікно на прикладання картки */
    TMR_CONTACTOR_SETTLE,  /* перехідні процеси після замикання контактора */
    TMR_FAULT_LOCKOUT,     /* мінімальне утримання в аварії */
    TMR_CP_RECHECK,        /* повторна перевірка пілота */
    TMR_COUNT
} soft_timer_id_t;

void soft_timer_init(void);

/* Звести таймер на delay_ms уперед від поточного моменту. Повторний виклик
 * перезводить його, а не заводить другий. */
void soft_timer_arm(soft_timer_id_t id, uint32_t delay_ms);

void soft_timer_disarm(soft_timer_id_t id);
bool soft_timer_is_armed(soft_timer_id_t id);

/*
 * Викликається з обробника системного таймера кожну мілісекунду. Робить рівно
 * дві дії — порівнює терміни й штовхає EVT_TIMEOUT у чергу, — тож лишається
 * придатною для виконання в перериванні.
 */
void soft_timer_tick(uint32_t now_ms);

#endif /* EVSE_SOFT_TIMER_H */
