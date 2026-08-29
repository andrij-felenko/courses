/* ==========================================================================
 *  mag_cal_fsm.c — переходи автомата, гейти якості й запис у Flash
 * ========================================================================== */

#include <math.h>

#include "mag_cal_fsm.h"
#include "mag_cal_linalg.h"

/* Радіус підігнаної сфери, що розійшовся з очікуваним полем більше ніж на
 * третину, майже завжди означає калібрування біля сталевої конструкції. */
#define MAG_CAL_RADIUS_TOLERANCE 0.30f

const char *mag_cal_state_str(mag_cal_state_t st) {
    switch (st) {
        case MAG_CAL_STATE_IDLE:       return "IDLE";
        case MAG_CAL_STATE_COLLECTING: return "COLLECTING";
        case MAG_CAL_STATE_SOLVING:    return "SOLVING";
        case MAG_CAL_STATE_VALIDATING: return "VALIDATING";
        case MAG_CAL_STATE_REJECTED:   return "REJECT";
        case MAG_CAL_STATE_SAVED:      return "SAVED";
        default:                       return "?";
    }
}

static void mag_cal_enter(mag_cal_fsm_t *fsm, mag_cal_state_t st, uint32_t now_ms) {
    fsm->state          = st;
    fsm->state_since_ms = now_ms;
}

/* Прапорець відмови й діод завжди рухаються разом: інакше на борту буває
 * стан, коли стек знає про несправність, а зовні цього не видно. */
static void mag_cal_set_fault(mag_cal_fsm_t *fsm, bool fault) {
    fsm->mag_fault = fault;
    mag_cal_board_fault_led(fault);
}

void mag_cal_fsm_init(mag_cal_fsm_t *fsm, uint8_t compass_id,
                      uint8_t system_id, uint8_t component_id,
                      float earth_field_ut) {
    mag_cal_collector_init(&fsm->collector, earth_field_ut);
    mag_cal_telemetry_init(&fsm->tm, system_id, component_id, compass_id);

    fsm->active               = MAG_CAL_IDENTITY_RESULT;
    fsm->active.earth_field   = fsm->collector.target_earth_field;
    fsm->active.compass_id    = compass_id;
    fsm->candidate            = fsm->active;
    fsm->last_solve           = MAG_CAL_SOLVE_OK;
    fsm->last_storage         = MAG_CAL_STORAGE_OK;
    fsm->state                = MAG_CAL_STATE_IDLE;
    fsm->state_since_ms       = 0;
    fsm->mag_fault            = true;   /* доки Flash не прочитано — відмова */
}

mag_cal_storage_status_t mag_cal_fsm_boot(mag_cal_fsm_t *fsm, uint32_t now_ms) {
    mag_cal_result_t loaded;
    const mag_cal_storage_status_t st = mag_cal_storage_load(&loaded);

    fsm->last_storage = st;
    if (st == MAG_CAL_STORAGE_OK) {
        loaded.compass_id = fsm->tm.compass_id;
        fsm->active       = loaded;
        mag_cal_set_fault(fsm, false);
    } else {
        /* Биті або відсутні коефіцієнти: летимо на сирому компасі лише
         * після усвідомленого рішення оператора, тож піднімаємо відмову. */
        fsm->active             = MAG_CAL_IDENTITY_RESULT;
        fsm->active.compass_id  = fsm->tm.compass_id;
        fsm->active.earth_field = fsm->collector.target_earth_field;
        mag_cal_set_fault(fsm, true);
    }

    mag_cal_enter(fsm, MAG_CAL_STATE_IDLE, now_ms);
    return st;
}

bool mag_cal_fsm_start(mag_cal_fsm_t *fsm, uint32_t now_ms) {
    if (fsm->state == MAG_CAL_STATE_COLLECTING ||
        fsm->state == MAG_CAL_STATE_SOLVING ||
        fsm->state == MAG_CAL_STATE_VALIDATING) {
        return false;               /* процедура вже йде */
    }

    mag_cal_collector_init(&fsm->collector, fsm->active.earth_field);
    fsm->collector.last_accept_ms = now_ms;   /* відлік тайм-ауту від старту */
    mag_cal_telemetry_next_attempt(&fsm->tm);
    mag_cal_enter(fsm, MAG_CAL_STATE_COLLECTING, now_ms);

    (void)mag_cal_telemetry_progress(&fsm->tm, &fsm->collector,
                                     MAG_CAL_TM_WAITING, now_ms);
    return true;
}

void mag_cal_fsm_cancel(mag_cal_fsm_t *fsm, uint32_t now_ms) {
    if (fsm->state == MAG_CAL_STATE_IDLE) {
        return;
    }

    /* Скидаємо хмару й повертаємо ті коефіцієнти, з якими апарат літав:
     * саме з Flash, а не з оперативної копії — так відкат перевіряє ще й
     * те, що збережений запис і далі читається. */
    mag_cal_collector_init(&fsm->collector, fsm->active.earth_field);

    mag_cal_result_t restored;
    fsm->last_storage = mag_cal_storage_load(&restored);
    if (fsm->last_storage == MAG_CAL_STORAGE_OK) {
        restored.compass_id = fsm->tm.compass_id;
        fsm->active = restored;
        mag_cal_set_fault(fsm, false);
    } else {
        mag_cal_set_fault(fsm, true);
    }

    mag_cal_telemetry_report(&fsm->tm, &fsm->active, false, false);
    mag_cal_enter(fsm, MAG_CAL_STATE_IDLE, now_ms);
}

bool mag_cal_fsm_push(mag_cal_fsm_t *fsm, vec3_t raw, vec3_t gyro_rad_s,
                      uint32_t now_ms) {
    if (fsm->state != MAG_CAL_STATE_COLLECTING) {
        return false;
    }
    return mag_cal_collector_push(&fsm->collector, raw, gyro_rad_s, now_ms);
}

bool mag_cal_fsm_ready_to_solve(const mag_cal_fsm_t *fsm) {
    if (fsm->state != MAG_CAL_STATE_COLLECTING) {
        return false;
    }
    return mag_cal_collector_coverage(&fsm->collector) >= MAG_CAL_SOLVE_COVERAGE_PCT
        && fsm->collector.total_points >= MAG_CAL_MIN_POINTS;
}

void mag_cal_fsm_begin_solve(mag_cal_fsm_t *fsm, uint32_t now_ms) {
    if (fsm->state == MAG_CAL_STATE_COLLECTING) {
        mag_cal_enter(fsm, MAG_CAL_STATE_SOLVING, now_ms);
    }
}

void mag_cal_fsm_submit(mag_cal_fsm_t *fsm, mag_cal_solve_status_t status,
                        const mag_cal_result_t *result, uint32_t now_ms) {
    if (fsm->state != MAG_CAL_STATE_SOLVING) {
        return;                     /* результат від скасованої спроби */
    }

    fsm->last_solve            = status;
    fsm->candidate             = *result;
    fsm->candidate.compass_id  = fsm->tm.compass_id;

    if (status != MAG_CAL_SOLVE_OK) {
        /* Гілка REJECT діаграми: чинні коефіцієнти лишаються ті, що були */
        const float ratio = (fsm->candidate.earth_field > 1.0f)
                          ? (fsm->candidate.sphere_radius / fsm->candidate.earth_field)
                          : 1.0f;
        const bool bad_radius = fabsf(ratio - 1.0f) > MAG_CAL_RADIUS_TOLERANCE;

        mag_cal_enter(fsm, MAG_CAL_STATE_REJECTED, now_ms);
        (void)mag_cal_telemetry_progress(&fsm->tm, &fsm->collector,
                                         bad_radius ? MAG_CAL_TM_BAD_RADIUS
                                                    : MAG_CAL_TM_FAILED,
                                         now_ms);
        mag_cal_telemetry_report(&fsm->tm, &fsm->candidate, false, false);
        return;
    }

    /* Нев'язка пройшла — переходимо до перевірки геометрії матриці W */
    mag_cal_enter(fsm, MAG_CAL_STATE_VALIDATING, now_ms);

    if (fsm->candidate.condition_num >= MAG_CAL_MAX_CONDITION) {
        mag_cal_enter(fsm, MAG_CAL_STATE_REJECTED, now_ms);
        mag_cal_telemetry_report(&fsm->tm, &fsm->candidate, false, false);
        return;
    }

    const mag_cal_storage_status_t saved = mag_cal_storage_save(&fsm->candidate);
    fsm->last_storage = saved;
    if (saved != MAG_CAL_STORAGE_OK) {
        /* Порахували добре, а зберегти не змогли: приймати такі коефіцієнти
         * в оперативну пам'ять не можна — після перезавантаження апарат
         * полетів би з іншими, і причину шукали б у повітрі. */
        mag_cal_enter(fsm, MAG_CAL_STATE_REJECTED, now_ms);
        mag_cal_telemetry_report(&fsm->tm, &fsm->candidate, false, false);
        return;
    }

    fsm->active = fsm->candidate;
    mag_cal_set_fault(fsm, false);
    mag_cal_enter(fsm, MAG_CAL_STATE_SAVED, now_ms);
    mag_cal_telemetry_report(&fsm->tm, &fsm->active, true, true);
}

void mag_cal_fsm_service(mag_cal_fsm_t *fsm, uint32_t now_ms) {
    switch (fsm->state) {
        case MAG_CAL_STATE_COLLECTING: {
            const uint32_t idle = now_ms - fsm->collector.last_accept_ms;
            if (idle > MAG_CAL_IDLE_TIMEOUT_MS) {
                mag_cal_fsm_cancel(fsm, now_ms);
                return;
            }
            (void)mag_cal_telemetry_progress(&fsm->tm, &fsm->collector,
                                             MAG_CAL_TM_COLLECTING, now_ms);
            break;
        }
        case MAG_CAL_STATE_SOLVING:
        case MAG_CAL_STATE_VALIDATING:
            (void)mag_cal_telemetry_progress(&fsm->tm, &fsm->collector,
                                             MAG_CAL_TM_SOLVING, now_ms);
            break;

        case MAG_CAL_STATE_SAVED:
            (void)mag_cal_telemetry_progress(&fsm->tm, &fsm->collector,
                                             MAG_CAL_TM_SUCCESS, now_ms);
            break;

        case MAG_CAL_STATE_REJECTED:
            (void)mag_cal_telemetry_progress(&fsm->tm, &fsm->collector,
                                             MAG_CAL_TM_FAILED, now_ms);
            break;

        case MAG_CAL_STATE_IDLE:
        default:
            break;
    }
}

vec3_t mag_cal_fsm_correct(const mag_cal_fsm_t *fsm, vec3_t raw) {
    return mag_cal_apply(raw, &fsm->active);
}

bool mag_cal_fsm_arming_allowed(const mag_cal_fsm_t *fsm) {
    /* Озброєння блокує і відмова компаса, і сама незавершена процедура:
     * крутити апарат у руках із розкрученими двигунами нікому не треба. */
    if (fsm->mag_fault || !fsm->active.is_valid) {
        return false;
    }
    return fsm->state == MAG_CAL_STATE_IDLE
        || fsm->state == MAG_CAL_STATE_SAVED
        || fsm->state == MAG_CAL_STATE_REJECTED;
}
