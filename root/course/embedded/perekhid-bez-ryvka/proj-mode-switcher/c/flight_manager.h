#ifndef FLIGHT_MANAGER_H
#define FLIGHT_MANAGER_H

#include <stdbool.h>
#include <stdint.h>

#include "pid.h"

typedef enum {
    MODE_MANUAL = 0,
    MODE_ALT_HOLD,
    MODE_AUTO_MISSION
} flight_mode_t;

/* Підказка пілоту на екран пульта чи світлодіод. */
typedef enum {
    HINT_NONE = 0,
    HINT_STICK_UP,       /* ручка нижче за утримувану тягу — піднімай */
    HINT_STICK_DOWN,     /* ручка вище — опускай */
    HINT_STICK_MATCHED   /* зійшлися, керування віддано */
} stick_hint_t;

/* Те, що дала фузія сенсорів на цьому такті. */
typedef struct {
    float alt_m;
    float climb_mps;
    float heading_deg;
} vehicle_state_t;

/* Те, що прийшло з пульта. */
typedef struct {
    float throttle;       /* 0..1 */
    int   mode_pos;       /* 0..2 з AUX1 */
    bool  force_override; /* AUX2 — силове перехоплення */
    bool  valid;          /* лінк живий */
} pilot_input_t;

typedef struct {
    float        throttle;        /* частка 0..1 на ESC */
    uint16_t     dshot_value;     /* 11-бітне значення */
    uint16_t     dshot_packet;    /* готове слово на дріт */
    float        heading_cmd_deg;
    stick_hint_t hint;
} fm_output_t;

typedef struct {
    flight_mode_t mode;
    pid_t alt_pid;
    pid_t mission_pid;
    float last_out;

    bool  stick_hold;     /* Stick Matching: тримаємо тягу самі */
    float u_hold;

    bool  failsafe;
    bool  armed;

    float mission_alt_m;
    float home_alt_m;
    float home_bearing_deg;
    float heading_cmd_deg;

    unsigned handover_warnings; /* захоплення з ненульовим стрибком */
    unsigned rejected_switches; /* перемикання, яким відмовили */
} flight_manager_t;

void fm_init(flight_manager_t *m, float home_alt_m, float home_bearing_deg);
void fm_set_armed(flight_manager_t *m, bool armed);
void fm_set_mission_target(flight_manager_t *m, float alt_m);

bool fm_request_mode(flight_manager_t *m, flight_mode_t mode, const vehicle_state_t *st);
void fm_enter_failsafe(flight_manager_t *m, const vehicle_state_t *st);
void fm_clear_failsafe(flight_manager_t *m);

fm_output_t fm_step(flight_manager_t *m, const pilot_input_t *rc,
                    const vehicle_state_t *st, float dt);

const char *fm_mode_name(flight_mode_t mode);
const char *fm_hint_text(stick_hint_t hint);

#endif /* FLIGHT_MANAGER_H */
