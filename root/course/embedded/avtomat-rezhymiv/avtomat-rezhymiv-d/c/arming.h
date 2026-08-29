#ifndef FM_ARMING_H
#define FM_ARMING_H

#include <stdbool.h>

#include "debounce.h"
#include "guards.h"
#include "params.h"
#include "telemetry.h"

/* Детектор польоту й арбітр роззброєння. Ці дві речі нероздільні: заборона
   роззброїтися в повітрі має сенс рівно настільки, наскільки чесно автомат
   знає, що апарат таки в повітрі. */
typedef struct {
    fm_debounce_t in_air;   /* витриманий вердикт «у повітрі»                  */
    bool          armed;    /* чи генеруються сигнали на регулятори            */
    bool          kill_latched; /* апаратна відсічка спрацювала — назад не буває */
} fm_arming_t;

void fm_arming_init(fm_arming_t *a, bool armed);

/* Один такт детектора польоту. Повертає витриманий вердикт «у повітрі».
   Ознак три — висота над точкою старту, оберти вище холостого ходу й
   ненульова динаміка прискорень; жодна поодинці не переконлива. */
bool fm_arming_update(fm_arming_t *a, const fm_state_t *s, const fm_params_t *p);

/* Детектор посадки підтвердив, що апарат стоїть: знімаємо вердикт польоту
   негайно, не чекаючи витримки згасання. */
void fm_arming_notify_landed(fm_arming_t *a, const fm_state_t *s);

bool fm_arming_in_air(const fm_arming_t *a);
bool fm_arming_is_armed(const fm_arming_t *a);

/* Запит на роззброєння комбінацією стіків або командою MAVLink.
   У повітрі — відмова, і це не налаштовується. */
fm_deny_t fm_arming_request_disarm(fm_arming_t *a, const fm_state_t *s);

/* Роззброєння за рішенням автомата: детектор посадки підтвердив контакт із
   ґрунтом і витримку. Обходить перевірку «у повітрі» законно. */
void fm_arming_disarm_after_landing(fm_arming_t *a, const fm_state_t *s);

/* Апаратна відсічка: єдиний шлях зупинити мотори в польоті. Тумблер працює в
   обхід автомата — тут ми лише приводимо власну картину світу у відповідність
   до того, що вже сталося на рівні співпроцесора вводу-виводу. */
void fm_arming_kill(fm_arming_t *a);

/* Спроба озброїтися на землі; у повітрі беззмістовна, тому теж під охоронцем. */
fm_deny_t fm_arming_request_arm(fm_arming_t *a, const fm_state_t *s, const fm_params_t *p);

#endif /* FM_ARMING_H */
