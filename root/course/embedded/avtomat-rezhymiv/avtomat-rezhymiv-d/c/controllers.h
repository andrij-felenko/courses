#ifndef FM_CONTROLLERS_H
#define FM_CONTROLLERS_H

#include <stdbool.h>
#include <stdint.h>

#include "land_detector.h"
#include "modes.h"
#include "params.h"
#include "telemetry.h"
#include "throttle.h"

/* Набір контурів, які вмикає й вимикає автомат режимів. Модуль існує заради
   однієї властивості — безривкового переходу: у момент зміни режиму цільові
   уставки прирівнюються до поточних значень, а інтегратор вертикального каналу
   передустановлюється тягою висіння. Без цього перший же такт нового режиму
   видав би стрибок керуючого сигналу. */
typedef struct {
    /* Вертикальний канал */
    bool  alt_engaged;
    float alt_target_m;
    float vz_integrator;      /* у частках тяги, 0..1                          */

    /* Горизонтальний канал */
    bool    pos_engaged;
    bool    pos_latched;      /* ціль зафіксовано (стіки в нейтралі)           */
    int32_t target_lat_1e7;
    int32_t target_lon_1e7;
    float   vel_int_north;    /* інтегратори контуру швидкості, градуси нахилу */
    float   vel_int_east;
    float   tilt_north_deg;   /* поточна команда нахилу                        */
    float   tilt_east_deg;

    /* Вихід на мотори */
    fm_slew_t throttle_slew;
    float     output;
} fm_controllers_t;

void fm_ctl_init(fm_controllers_t *c, const fm_state_t *s);

/* Вхід у режим: фіксація уставок і передустановка інтеграторів. Викликається
   рівно один раз на перехід — ПІСЛЯ того, як охоронці дали дозвіл. */
void fm_ctl_enter_mode(fm_controllers_t *c, fm_mode_t mode,
                       const fm_state_t *s, const fm_params_t *p);

/* Зовнішня цілевказівка для Guided; поза Guided ігнорується. */
void fm_ctl_set_position_target(fm_controllers_t *c, fm_mode_t mode,
                                int32_t lat_1e7, int32_t lon_1e7, float alt_rel_m);

/* Один такт контурів. Повертає тягу 0..1 після обмежувача швидкості наростання. */
float fm_ctl_step(fm_controllers_t *c, fm_mode_t mode, const fm_state_t *s,
                  const fm_params_t *p, const fm_land_detector_t *land, float dt_s);

#endif /* FM_CONTROLLERS_H */
