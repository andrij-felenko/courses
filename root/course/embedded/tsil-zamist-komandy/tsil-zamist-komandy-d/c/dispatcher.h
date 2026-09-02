#ifndef DISPATCHER_H
#define DISPATCHER_H

/* Диспетчер автономних цілей: черга фіксованого розміру, скінченний автомат
   життєвого циклу, витіснення за пріоритетом і зв'язок із планувальниками. */

#include "goal.h"
#include "preflight.h"

typedef struct {
    goal_t goal;
    goal_state_t state;
    float elapsed_sec;    /* накопичений час виконання; переживає витіснення */
    vec3_t resume_from;   /* точка, де ціль перервали (прогрес витісненої) */
    uint8_t replans;      /* скільки разів просили обхід */
    bool replan_pending;  /* треба сказати глобальному планувальнику перерахувати */
    goal_check_t verdict; /* чому відхилено або перервано */
} goal_slot_t;

typedef struct {
    goal_slot_t slots[GOAL_QUEUE_CAPACITY];
    flight_envelope_t env;
    int8_t active;         /* індекс активного слота або -1 */
    float active_hold_sec; /* скільки активна ціль тримається (таймер утримання) */
    uint32_t next_id;
    bool emergency_armed;  /* аварійну ціль уже згенеровано */
} goal_dispatcher_t;

/* Що диспетчер каже польотному контуру на цьому такті. */
typedef struct {
    bool has_goal;
    uint32_t goal_id;
    goal_type_t type;
    vec3_t setpoint;       /* точка, на яку веде локальний контролер */
    bool replan_requested; /* глобальному планувальнику: перерахуй маршрут */
} dispatch_out_t;

void dispatcher_init(goal_dispatcher_t *d, const flight_envelope_t *env);

/* Ставить ціль у чергу. Повертає присвоєний id або 0, якщо місця немає. */
uint32_t dispatcher_submit(goal_dispatcher_t *d, const goal_t *g);

/* Один такт диспетчеризації (0.5–2 Гц вистачає). out може бути NULL. */
void dispatcher_tick(goal_dispatcher_t *d,
                     const system_state_t *sys,
                     float dt_sec,
                     dispatch_out_t *out);

/* Локальний контролер побачив, що прохід заблоковано наглухо. */
void dispatcher_report_path_blocked(goal_dispatcher_t *d);

/* Оператор знімає ціль (наприклад, скасував завдання з пульта). */
bool dispatcher_cancel(goal_dispatcher_t *d, uint32_t goal_id);

/* Слот цілі за id або NULL, якщо такої в черзі вже немає. */
const goal_slot_t *dispatcher_find(const goal_dispatcher_t *d, uint32_t goal_id);

#endif /* DISPATCHER_H */
