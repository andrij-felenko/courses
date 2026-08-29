#ifndef FM_LAND_DETECTOR_H
#define FM_LAND_DETECTOR_H

#include <stdbool.h>
#include <stdint.h>

#include "debounce.h"
#include "params.h"
#include "telemetry.h"

/* Фази завершення польоту. Барометр біля землі бреше на метр-другий через
   екранний ефект, тож момент торкання визначають не висотою, а збігом трьох
   незалежних ознак, витриманих у часі. */
typedef enum {
    FM_LAND_IDLE = 0,        /* режим посадки не активний                      */
    FM_LAND_DESCENT,         /* керований спуск зі швидкістю LAND_SPEED        */
    FM_LAND_GROUND_CONTACT,  /* ознаки торкання зібралися, триває витримка     */
    FM_LAND_LANDED           /* посадку підтверджено, час гасити мотори        */
} fm_land_phase_t;

typedef struct {
    fm_land_phase_t phase;
    fm_debounce_t   contact;        /* витримка ознак торкання                 */
    uint32_t        contact_ms;     /* коли фаза контакту почалася             */
    bool            disarm_event;   /* EVENT_DISARM, чекає на забирання        */
} fm_land_detector_t;

void fm_land_init(fm_land_detector_t *d);

/* Скидання при виході з режимів посадки: недокручена витримка не має права
   пережити зміну режиму й спрацювати наступного разу. */
void fm_land_reset(fm_land_detector_t *d);

/* Один такт. landing_mode — чи активний зараз Land / EmergLand / фінальна фаза
   RTL; in_air — вердикт детектора польоту. */
void fm_land_update(fm_land_detector_t *d, const fm_state_t *s, const fm_params_t *p,
                    bool landing_mode, bool in_air);

/* Забирає подію роззброєння (одноразова: другий виклик поверне false). */
bool fm_land_take_disarm_event(fm_land_detector_t *d);

/* Цільова вертикальна швидкість фази спуску (відʼємна — вниз). */
float fm_land_target_vz(const fm_land_detector_t *d, const fm_params_t *p);

const char *fm_land_phase_name(fm_land_phase_t phase);

static inline bool fm_land_is_landed(const fm_land_detector_t *d)
{
    return d && d->phase == FM_LAND_LANDED;
}

#endif /* FM_LAND_DETECTOR_H */
