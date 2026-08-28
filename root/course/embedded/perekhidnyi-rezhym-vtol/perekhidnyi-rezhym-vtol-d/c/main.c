#include <stdbool.h>
#include <stdint.h>
#include <math.h>

typedef enum {
    VTOL_STATE_HOVER = 0,
    VTOL_STATE_TRANSITION_FW,
    VTOL_STATE_FIXED_WING,
    VTOL_STATE_TRANSITION_MC,
    VTOL_STATE_FAILSAFE_RECOVERY
} vtol_transition_state_t;

typedef struct {
    float v_blend_start;      /* Початок змішування рулів (м/с), напр. 6.0 */
    float v_stall;            /* Швидкість звалювання крила (м/с), напр. 13.0 */
    float v_trans;            /* Швидкість повного переходу (м/с), напр. 16.0 */
    float max_trans_time_s;   /* Максимальний таймаут переходу (с), напр. 12.0 */
    float max_sink_rate_mps;  /* Критична швидкість просідання (м/с), напр. 2.5 */
    float prespool_throttle;  /* Газ передрозкрутки при Back-Trans (0.0..1.0), напр. 0.20 */
} vtol_transition_params_t;

typedef struct {
    vtol_transition_state_t state;
    float transition_time_elapsed;
    float pusher_throttle_cmd;
    float lift_rotors_weight;
    float surfaces_blend_factor;
    bool emergency_assist_active;
} vtol_transition_controller_t;

static inline float clampf(float val, float min_val, float max_val) {
    if (val < min_val) return min_val;
    if (val > max_val) return max_val;
    return val;
}

void vtol_controller_init(vtol_transition_controller_t *ctrl) {
    ctrl->state = VTOL_STATE_HOVER;
    ctrl->transition_time_elapsed = 0.0f;
    ctrl->pusher_throttle_cmd = 0.0f;
    ctrl->lift_rotors_weight = 1.0f;
    ctrl->surfaces_blend_factor = 0.0f;
    ctrl->emergency_assist_active = false;
}

void vtol_controller_update(vtol_transition_controller_t *ctrl,
                            const vtol_transition_params_t *params,
                            float ias_mps,
                            float sink_rate_mps,
                            float dt_sec,
                            bool command_transition_to_fw,
                            bool command_transition_to_mc)
{
    switch (ctrl->state) {
    case VTOL_STATE_HOVER:
        ctrl->pusher_throttle_cmd = 0.0f;
        ctrl->lift_rotors_weight = 1.0f;
        ctrl->surfaces_blend_factor = 0.0f;
        ctrl->transition_time_elapsed = 0.0f;
        ctrl->emergency_assist_active = false;

        if (command_transition_to_fw) {
            ctrl->state = VTOL_STATE_TRANSITION_FW;
            ctrl->transition_time_elapsed = 0.0f;
        }
        break;

    case VTOL_STATE_TRANSITION_FW:
        ctrl->transition_time_elapsed += dt_sec;

        /* Повна тяга маршового штовхача для горизонтального розгону */
        ctrl->pusher_throttle_cmd = 1.0f;

        /* Захист 1: Перевірка небезпечного просідання (Altitude Sink Hole) */
        if (sink_rate_mps > params->max_sink_rate_mps) {
            ctrl->emergency_assist_active = true;
            ctrl->state = VTOL_STATE_FAILSAFE_RECOVERY;
            break;
        }

        /* Захист 2: Перевірка таймауту переходу (нестача тяги / відмова Піто) */
        if (ctrl->transition_time_elapsed > params->max_trans_time_s) {
            ctrl->emergency_assist_active = true;
            ctrl->state = VTOL_STATE_FAILSAFE_RECOVERY;
            break;
        }

        /* Розрахунок вагового коефіцієнта елеронів B(v) */
        if (ias_mps < params->v_blend_start) {
            ctrl->surfaces_blend_factor = 0.0f;
        } else {
            float range = params->v_trans - params->v_blend_start;
            ctrl->surfaces_blend_factor = clampf((ias_mps - params->v_blend_start) / range, 0.0f, 1.0f);
        }

        /* Квадратичне розвантаження вертикальних роторів: T_v = 1 - (v / v_trans)^2 */
        if (ias_mps >= params->v_trans) {
            ctrl->lift_rotors_weight = 0.0f;
            ctrl->pusher_throttle_cmd = 0.65f; /* Перехід на крейсерський газ */
            ctrl->surfaces_blend_factor = 1.0f;
            ctrl->state = VTOL_STATE_FIXED_WING;
        } else {
            float v_ratio = clampf(ias_mps / params->v_trans, 0.0f, 1.0f);
            float force_deficit = 1.0f - (v_ratio * v_ratio);
            /* Переведення сили в сигнал газу через корінь (лінеаризація ESC) */
            ctrl->lift_rotors_weight = sqrtf(force_deficit);
        }
        break;

    case VTOL_STATE_FIXED_WING:
        ctrl->pusher_throttle_cmd = 0.65f;
        ctrl->lift_rotors_weight = 0.0f;
        ctrl->surfaces_blend_factor = 1.0f;
        ctrl->transition_time_elapsed = 0.0f;
        ctrl->emergency_assist_active = false;

        if (command_transition_to_mc) {
            ctrl->state = VTOL_STATE_TRANSITION_MC;
            ctrl->transition_time_elapsed = 0.0f;
        }
        break;

    case VTOL_STATE_TRANSITION_MC:
        ctrl->transition_time_elapsed += dt_sec;
        ctrl->pusher_throttle_cmd = 0.0f; /* Вимкнення маршового двигуна */

        /* Холодна передрозкрутка роторів для усунення лагу розгону моторів */
        if (ias_mps > params->v_stall) {
            ctrl->lift_rotors_weight = params->prespool_throttle;
            ctrl->surfaces_blend_factor = 1.0f;
        } else {
            /* Швидкість впала нижче звалювання: повне перехоплення ваги роторами */
            float v_mc_ratio = clampf(ias_mps / params->v_stall, 0.0f, 1.0f);
            float weight = 1.0f - (v_mc_ratio * v_mc_ratio);
            ctrl->lift_rotors_weight = clampf(sqrtf(weight) + params->prespool_throttle, 0.0f, 1.0f);
            ctrl->surfaces_blend_factor = v_mc_ratio;
        }

        /* Завершення зворотного переходу при повній зупинці */
        if (ias_mps < params->v_blend_start) {
            ctrl->lift_rotors_weight = 1.0f;
            ctrl->surfaces_blend_factor = 0.0f;
            ctrl->state = VTOL_STATE_HOVER;
        }
        break;

    case VTOL_STATE_FAILSAFE_RECOVERY:
        /* Екстрене гасіння швидкості та повернення у висіння на 100% тязі роторів */
        ctrl->pusher_throttle_cmd = 0.0f;
        ctrl->lift_rotors_weight = 1.0f;
        ctrl->surfaces_blend_factor = 0.0f;

        if (ias_mps < params->v_blend_start && sink_rate_mps < 0.5f) {
            ctrl->emergency_assist_active = false;
            ctrl->state = VTOL_STATE_HOVER;
        }
        break;
    }
}
