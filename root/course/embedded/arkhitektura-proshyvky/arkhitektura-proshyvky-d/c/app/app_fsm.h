/* app/app_fsm.h — кінцевий автомат режимів логера.
 * Автомат навмисно стерильний: він приймає подію, повертає дію і не робить
 * жодного вводу-виводу. Саме тому весь набір переходів перевіряється
 * модульним тестом на комп'ютері розробника за мілісекунди, без плати,
 * без термофена і без осцилографа. */
#ifndef APP_FSM_H
#define APP_FSM_H

#include "include/event_types.h"

typedef enum {
    APP_STATE_BOOT = 0,
    APP_STATE_IDLE,      /* давачі підняті, запис призупинено */
    APP_STATE_SAMPLING,  /* штатний збір даних */
    APP_STATE_ALARM,     /* перевищено поріг, запис триває */
    APP_STATE_FAULT      /* давач не відповідає, потрібне втручання */
} app_state_t;

/* Що автомат просить зробити. Виконує ці дії координатор — автомат лише
 * називає їх, і тому лишається переносним. */
typedef enum {
    APP_ACTION_NONE = 0,
    APP_ACTION_START_SAMPLING,
    APP_ACTION_STOP_SAMPLING,
    APP_ACTION_SAMPLE_SENSORS,
    APP_ACTION_RAISE_ALARM,
    APP_ACTION_CLEAR_ALARM,
    APP_ACTION_ENTER_FAULT,
    APP_ACTION_RECOVER
} app_action_t;

typedef struct {
    app_state_t state;
    uint32_t    state_since_ms;
    uint32_t    consecutive_faults;
    uint32_t    fault_limit;
} app_fsm_t;

void app_fsm_init(app_fsm_t *fsm, uint32_t fault_limit);

/* Єдина точка переходів. Чиста функція стану й події. */
app_action_t app_fsm_dispatch(app_fsm_t *fsm, const sys_event_t *evt);

app_state_t app_fsm_state(const app_fsm_t *fsm);
const char *app_fsm_state_name(app_state_t state);
const char *app_fsm_action_name(app_action_t action);

#endif /* APP_FSM_H */
