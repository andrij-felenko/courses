#ifndef FM_FSM_H
#define FM_FSM_H

#include <stdbool.h>
#include <stdint.h>

#include "arming.h"
#include "controllers.h"
#include "debounce.h"
#include "failsafe.h"
#include "guards.h"
#include "land_detector.h"
#include "modes.h"
#include "params.h"
#include "report.h"
#include "telemetry.h"

/* Автомат польотних режимів. Уся мінлива правда про те, який контур зараз
   активний, живе тут і більше ніде: жодного глобального прапорця «ми в
   PosHold», який хтось поставить повз перевірку. */
typedef struct {
    fm_mode_t     mode;
    fm_mode_t     previous_mode;
    fm_priority_t mode_priority;   /* хто поставив поточний режим              */
    uint32_t      mode_since_ms;
    uint32_t      last_step_ms;
    bool          primed;

    fm_params_t   params;
    fm_reporter_t reporter;

    fm_arming_t        arming;
    fm_land_detector_t land;
    fm_controllers_t   ctl;

    /* Гістерезис охоронців: щоб автомат не деренчав, коли HDOP гойдається
       навколо порога, дозвіл на підйом угору ієрархією вимагає витримки. */
    fm_debounce_t alt_guard_ok;
    fm_debounce_t pos_guard_ok;

    const char *last_failsafe_reason;  /* аби не сипати той самий STATUSTEXT   */
    float       throttle_output;
} fm_fsm_t;

/* params і reporter копіюються в автомат; s потрібен, щоб перший такт стартував
   від справжніх показів, а не від нулів. */
void fm_fsm_init(fm_fsm_t *fsm, const fm_params_t *params,
                 const fm_reporter_t *reporter, const fm_state_t *s);

/* Штатний запит зміни режиму: тумблер пульта, MAV_CMD_DO_SET_MODE, перехоплення
   стіками. Повертає причину відмови; FM_ALLOW — режим змінено.
   Відмова АТОМАРНА: жодне поле автомата й жоден контур не зачеплено. */
fm_deny_t fm_fsm_request_mode(fm_fsm_t *fsm, fm_mode_t target,
                              fm_priority_t priority, const fm_state_t *s);

/* Один такт автомата: детектор польоту, арбітр аварій, перехоплення стіками,
   каскадна деградація, детектор посадки, контури. Викликається з 50–100 Гц. */
void fm_fsm_update(fm_fsm_t *fsm, const fm_state_t *s);

/* Запит озброєння на землі та роззброєння комбінацією стіків чи командою
   станції. Озброєння — теж перехід під охоронцем, а не перемикання прапорця. */
fm_deny_t fm_fsm_request_arm(fm_fsm_t *fsm, const fm_state_t *s);
fm_deny_t fm_fsm_request_disarm(fm_fsm_t *fsm, const fm_state_t *s);

/* Зовнішня цілевказівка для Guided / навігатора місії. */
void fm_fsm_set_position_target(fm_fsm_t *fsm, int32_t lat_1e7, int32_t lon_1e7,
                                float alt_rel_m);

fm_mode_t       fm_fsm_mode(const fm_fsm_t *fsm);
fm_priority_t   fm_fsm_priority(const fm_fsm_t *fsm);
float           fm_fsm_throttle(const fm_fsm_t *fsm);
bool            fm_fsm_in_air(const fm_fsm_t *fsm);
bool            fm_fsm_armed(const fm_fsm_t *fsm);
fm_land_phase_t fm_fsm_land_phase(const fm_fsm_t *fsm);

#endif /* FM_FSM_H */
