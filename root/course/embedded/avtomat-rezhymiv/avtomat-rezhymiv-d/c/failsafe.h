#ifndef FM_FAILSAFE_H
#define FM_FAILSAFE_H

#include <stdbool.h>
#include <stdint.h>

#include "modes.h"
#include "params.h"
#include "telemetry.h"

/* Сходинка пріоритетів. Число тут не декоративне: воно вирішує, чий запит
   переможе, коли за один такт до автомата приходять і тумблер пілота, і
   аварія живлення. */
typedef enum {
    FM_PRIO_NONE = 0,
    FM_PRIO_ROUTINE        = 1, /* тумблер RC або MAV_CMD_DO_SET_MODE           */
    FM_PRIO_PILOT_OVERRIDE = 2, /* рух стіків скасовує автономію                */
    FM_PRIO_NAV_FAILSAFE   = 3, /* втрата лінка, геозона, розряд Stage 1        */
    FM_PRIO_CRITICAL       = 4, /* Stage 2 живлення, крах оцінювачів            */
    FM_PRIO_HARDWARE       = 5  /* апаратна відсічка, парашут                   */
} fm_priority_t;

typedef struct {
    bool          active;
    fm_priority_t priority;
    fm_mode_t     mode;      /* режим, у який витісняється апарат               */
    uint8_t       severity;  /* MAV_SEVERITY_* для STATUSTEXT                   */
    const char   *reason;    /* готовий текст причини                           */
} fm_preempt_t;

/* Чи має право запит пріоритету request витіснити стан, установлений
   пріоритетом active. Рівень 3 пілот перехоплює, рівень 4 — уже ні. */
bool fm_priority_overrides(fm_priority_t request, fm_priority_t active);

const char *fm_priority_name(fm_priority_t prio);

/* Арбітр аварій: єдина точка, де народжуються витіснення. Функція чиста —
   вона лише читає стан і повертає рішення, а міняє режим автомат. */
fm_preempt_t fm_failsafe_evaluate(const fm_state_t *s, const fm_params_t *p,
                                  fm_mode_t current, bool in_air);

/* Порушення геозони — окремо, бо ту саму перевірку показує телеметрія. */
bool fm_failsafe_fence_breached(const fm_state_t *s, const fm_params_t *p);

#endif /* FM_FAILSAFE_H */
