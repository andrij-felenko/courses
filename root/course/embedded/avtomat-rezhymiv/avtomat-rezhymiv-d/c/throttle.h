#ifndef FM_THROTTLE_H
#define FM_THROTTLE_H

#include <stdbool.h>

#include "guards.h"
#include "modes.h"
#include "params.h"
#include "telemetry.h"

/* Заслінка газу — інтерлок, що не дає ручці стрибнути замість регулятора.
   Перехід з режиму з автоматичною тягою в режим прямої тяги дозволено лише
   тоді, коли фізичне положення стіка вже збігається з тим, що видає
   регулятор; інакше вихід стрибне з тяги висіння в нуль за один такт. */
fm_deny_t fm_throttle_interlock(fm_mode_t current, fm_mode_t target,
                                const fm_state_t *s, const fm_params_t *p,
                                bool in_air);

/* Наскільки стік розходиться з поточною тягою (0..1). Потрібне як для
   інтерлока, так і для підказки пілотові в телеметрії. */
float fm_throttle_mismatch(const fm_state_t *s);

/* Обмежувач швидкості наростання тяги: навіть після дозволеного переходу вихід
   не має права змінюватися стрибком. Стан — одне число, попередній вихід. */
typedef struct {
    float output;
    bool  primed;
} fm_slew_t;

void  fm_slew_reset(fm_slew_t *sl, float value);
float fm_slew_step(fm_slew_t *sl, float target, float dt_s, float rate_per_s);

#endif /* FM_THROTTLE_H */
