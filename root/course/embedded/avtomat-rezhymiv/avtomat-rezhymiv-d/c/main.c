#include <stdbool.h>
#include <stdint.h>
#include <string.h>

/* Перелік польотних режимів автопілота */
typedef enum {
    FLIGHT_MODE_MANUAL = 0,
    FLIGHT_MODE_STABILIZE,
    FLIGHT_MODE_ALT_HOLD,
    FLIGHT_MODE_POS_HOLD,
    FLIGHT_MODE_AUTO,
    FLIGHT_MODE_GUIDED,
    FLIGHT_MODE_RTL,
    FLIGHT_MODE_LAND,
    FLIGHT_MODE_EMERGENCY_LAND,
    FLIGHT_MODE_TERMINATE,
    FLIGHT_MODE_COUNT
} FlightMode;

/* Коди результатів запиту на зміну режиму (MAVLink сумісні) */
typedef enum {
    TRANSITION_OK = 0,
    TRANSITION_DENIED_NO_GPS,
    TRANSITION_DENIED_BAD_HDOP,
    TRANSITION_DENIED_EKF_UNHEALTHY,
    TRANSITION_DENIED_NO_MISSION,
    TRANSITION_DENIED_NO_HOME,
    TRANSITION_DENIED_THROTTLE_MISMATCH,
    TRANSITION_DENIED_FAILSAFE_ACTIVE,
    TRANSITION_DENIED_INVALID_MODE
} TransitionResult;

/* Структура знімка стану сенсорів та телеметрії */
typedef struct {
    bool armed;
    bool in_air;
    uint8_t gps_fix_type;      /* 0: No Fix, 2: 2D, 3: 3D Fix */
    uint8_t gps_num_sats;
    float gps_hdop;
    float gps_vdop;
    bool ekf_pos_horiz_valid;
    bool ekf_pos_vert_valid;
    float ekf_innov_pos;
    bool compass_healthy;
    uint16_t mission_item_count;
    bool home_position_set;
    float current_throttle;    /* 0.0f - 1.0f поточний вихід регулятора */
    float stick_throttle;      /* 0.0f - 1.0f положення ручки на пульті */
    float vertical_velocity;   /* м/с, додатна вгору */
    bool rc_link_lost;
    bool gcs_link_lost;
    uint8_t battery_failsafe_stage; /* 0: OK, 1: Low, 2: Critical */
    bool hardware_kill_switch;
} TelemetrySnapshot;

/* Стан детектора посадки */
typedef struct {
    bool ground_contact;
    bool landed;
    uint32_t contact_start_ms;
} LandDetector;

/* Стан автомата режимів */
typedef struct {
    FlightMode current_mode;
    FlightMode previous_mode;
    uint32_t last_transition_ms;
    bool failsafe_locked;
    LandDetector land_detector;
} FlightModeFSM;

/* Ініціалізація автомата польотних режимів */
void fsm_init(FlightModeFSM* fsm) {
    if (!fsm) return;
    fsm->current_mode = FLIGHT_MODE_STABILIZE;
    fsm->previous_mode = FLIGHT_MODE_STABILIZE;
    fsm->last_transition_ms = 0;
    fsm->failsafe_locked = false;
    fsm->land_detector.ground_contact = false;
    fsm->land_detector.landed = false;
    fsm->land_detector.contact_start_ms = 0;
}

/* Умова-охоронець для режиму PosHold / Loiter */
static TransitionResult guard_pos_hold(const TelemetrySnapshot* t) {
    if (t->gps_fix_type < 3 || t->gps_num_sats < 6) {
        return TRANSITION_DENIED_NO_GPS;
    }
    if (t->gps_hdop > 1.5f || t->gps_vdop > 2.0f) {
        return TRANSITION_DENIED_BAD_HDOP;
    }
    if (!t->ekf_pos_horiz_valid || !t->compass_healthy || t->ekf_innov_pos > 0.3f) {
        return TRANSITION_DENIED_EKF_UNHEALTHY;
    }
    return TRANSITION_OK;
}

/* Умова-охоронець для режиму Auto */
static TransitionResult guard_auto(const TelemetrySnapshot* t) {
    TransitionResult pos_res = guard_pos_hold(t);
    if (pos_res != TRANSITION_OK) {
        return pos_res;
    }
    if (t->mission_item_count == 0) {
        return TRANSITION_DENIED_NO_MISSION;
    }
    if (!t->home_position_set) {
        return TRANSITION_DENIED_NO_HOME;
    }
    return TRANSITION_OK;
}

/* Умова-охоронець для режиму RTL */
static TransitionResult guard_rtl(const TelemetrySnapshot* t) {
    if (!t->home_position_set) {
        return TRANSITION_DENIED_NO_HOME;
    }
    if (!t->ekf_pos_horiz_valid && !t->ekf_pos_vert_valid) {
        return TRANSITION_DENIED_EKF_UNHEALTHY;
    }
    return TRANSITION_OK;
}

/* Захист від стрибка газу при переході з автоматичних режимів у ручні */
static bool check_throttle_matching(FlightMode current, FlightMode target, const TelemetrySnapshot* t) {
    bool is_current_auto_thrust = (current == FLIGHT_MODE_ALT_HOLD ||
                                   current == FLIGHT_MODE_POS_HOLD ||
                                   current == FLIGHT_MODE_AUTO ||
                                   current == FLIGHT_MODE_GUIDED ||
                                   current == FLIGHT_MODE_LAND ||
                                   current == FLIGHT_MODE_RTL);

    bool is_target_manual_thrust = (target == FLIGHT_MODE_MANUAL ||
                                    target == FLIGHT_MODE_STABILIZE);

    if (t->in_air && is_current_auto_thrust && is_target_manual_thrust) {
        float diff = t->stick_throttle - t->current_throttle;
        if (diff < 0.0f) diff = -diff;
        /* Дозволений поріг неспівпадіння: 15% */
        if (diff > 0.15f) {
            return false;
        }
    }
    return true;
}

/* Детектор посадки: виявлення контакту з ґрунтом */
static void update_land_detector(FlightModeFSM* fsm, const TelemetrySnapshot* t, uint32_t now_ms) {
    if (!t->in_air || (fsm->current_mode != FLIGHT_MODE_LAND && fsm->current_mode != FLIGHT_MODE_EMERGENCY_LAND)) {
        fsm->land_detector.ground_contact = false;
        fsm->land_detector.landed = false;
        fsm->land_detector.contact_start_ms = 0;
        return;
    }

    float vz_abs = t->vertical_velocity < 0.0f ? -t->vertical_velocity : t->vertical_velocity;
    bool vz_stopped = vz_abs < 0.25f;
    bool throttle_min = t->current_throttle < 0.20f;

    if (vz_stopped && throttle_min) {
        if (!fsm->land_detector.ground_contact) {
            fsm->land_detector.ground_contact = true;
            fsm->land_detector.contact_start_ms = now_ms;
        } else if (now_ms - fsm->land_detector.contact_start_ms > 1500) {
            fsm->land_detector.landed = true;
        }
    } else {
        fsm->land_detector.ground_contact = false;
        fsm->land_detector.contact_start_ms = 0;
    }
}

/* Арбітраж аварійних станів: перевірка умов вищого пріоритету */
static bool check_failsafe_preemption(FlightModeFSM* fsm, const TelemetrySnapshot* t, uint32_t now_ms) {
    /* Рівень 5: Hardware Kill Switch */
    if (t->hardware_kill_switch) {
        fsm->previous_mode = fsm->current_mode;
        fsm->current_mode = FLIGHT_MODE_TERMINATE;
        fsm->failsafe_locked = true;
        fsm->last_transition_ms = now_ms;
        return true;
    }

    /* Рівень 4: Критичний Failsafe батареї або повний крах навігації під час посадки */
    if (t->battery_failsafe_stage >= 2 && fsm->current_mode != FLIGHT_MODE_EMERGENCY_LAND) {
        fsm->previous_mode = fsm->current_mode;
        fsm->current_mode = FLIGHT_MODE_EMERGENCY_LAND;
        fsm->failsafe_locked = true;
        fsm->last_transition_ms = now_ms;
        return true;
    }

    /* Рівень 3: Втрата зв'язку RC або геозона -> RTL */
    if (t->rc_link_lost && t->in_air) {
        if (fsm->current_mode != FLIGHT_MODE_RTL && fsm->current_mode != FLIGHT_MODE_LAND &&
            fsm->current_mode != FLIGHT_MODE_EMERGENCY_LAND) {
            if (guard_rtl(t) == TRANSITION_OK) {
                fsm->previous_mode = fsm->current_mode;
                fsm->current_mode = FLIGHT_MODE_RTL;
                fsm->last_transition_ms = now_ms;
                return true;
            } else {
                /* Каскадна деградація: немає умов для RTL -> негайна посадка Land */
                fsm->previous_mode = fsm->current_mode;
                fsm->current_mode = FLIGHT_MODE_LAND;
                fsm->last_transition_ms = now_ms;
                return true;
            }
        }
    }
    return false;
}

/* Запит на штатну зміну режиму від оператора чи GCS */
TransitionResult fsm_request_mode(FlightModeFSM* fsm, FlightMode target, const TelemetrySnapshot* t, uint32_t now_ms) {
    if (!fsm || !t) return TRANSITION_DENIED_INVALID_MODE;

    /* Якщо активне блокування критичного Failsafe — штатні запити відхиляються */
    if (fsm->failsafe_locked && target != FLIGHT_MODE_STABILIZE) {
        return TRANSITION_DENIED_FAILSAFE_ACTIVE;
    }

    if (target == fsm->current_mode) {
        return TRANSITION_OK;
    }

    /* 1. Перевірка заслінки газу (захист від стрибка тяги) */
    if (!check_throttle_matching(fsm->current_mode, target, t)) {
        return TRANSITION_DENIED_THROTTLE_MISMATCH;
    }

    /* 2. Перевірка параметричних охоронців цільового режиму */
    TransitionResult res = TRANSITION_OK;
    switch (target) {
        case FLIGHT_MODE_MANUAL:
        case FLIGHT_MODE_STABILIZE:
            /* Базові ручні режими не вимагають зовнішніх сенсорів навігації */
            res = TRANSITION_OK;
            break;

        case FLIGHT_MODE_ALT_HOLD:
            if (!t->ekf_pos_vert_valid) {
                res = TRANSITION_DENIED_EKF_UNHEALTHY;
            }
            break;

        case FLIGHT_MODE_POS_HOLD:
        case FLIGHT_MODE_GUIDED:
            res = guard_pos_hold(t);
            break;

        case FLIGHT_MODE_AUTO:
            res = guard_auto(t);
            break;

        case FLIGHT_MODE_RTL:
            res = guard_rtl(t);
            break;

        case FLIGHT_MODE_LAND:
        case FLIGHT_MODE_EMERGENCY_LAND:
            res = TRANSITION_OK;
            break;

        default:
            res = TRANSITION_DENIED_INVALID_MODE;
            break;
    }

    if (res == TRANSITION_OK) {
        fsm->previous_mode = fsm->current_mode;
        fsm->current_mode = target;
        fsm->last_transition_ms = now_ms;
        fsm->failsafe_locked = false; /* Скидання блокування при свідомому виборі пілота */
    }

    return res;
}

/* Головний періодичний крок автомата (викликається з частотою 50-100 Гц) */
void fsm_update(FlightModeFSM* fsm, const TelemetrySnapshot* t, uint32_t now_ms) {
    if (!fsm || !t) return;

    /* 1. Оновлення детектора посадки */
    update_land_detector(fsm, t, now_ms);

    /* 2. Обробка аварійних витіснень */
    if (check_failsafe_preemption(fsm, t, now_ms)) {
        return;
    }

    /* 3. Каскадна деградація сенсорів у польоті */
    if (t->in_air) {
        if (fsm->current_mode == FLIGHT_MODE_POS_HOLD || fsm->current_mode == FLIGHT_MODE_AUTO) {
            if (guard_pos_hold(t) != TRANSITION_OK) {
                /* Деградація: PosHold/Auto -> AltHold */
                fsm->previous_mode = fsm->current_mode;
                fsm->current_mode = FLIGHT_MODE_ALT_HOLD;
                fsm->last_transition_ms = now_ms;
            }
        }

        if (fsm->current_mode == FLIGHT_MODE_ALT_HOLD) {
            if (!t->ekf_pos_vert_valid) {
                /* Деградація: AltHold -> Stabilize */
                fsm->previous_mode = fsm->current_mode;
                fsm->current_mode = FLIGHT_MODE_STABILIZE;
                fsm->last_transition_ms = now_ms;
            }
        }
    }
}
