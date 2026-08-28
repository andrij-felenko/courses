#include <stdbool.h>
#include <math.h>

typedef enum {
    DOCK_STAGE_IDLE = 0,
    DOCK_STAGE_CHECK_POWER,
    DOCK_STAGE_PRE_TORQUE,
    DOCK_STAGE_REVERSE_CORRIDOR,
    DOCK_STAGE_UNMOORING_BURST,
    DOCK_STAGE_TRACTION_VALIDATE,
    DOCK_STAGE_HEADING_ALIGN,
    DOCK_STAGE_SUCCESS,
    DOCK_STAGE_ABORT_FAULT
} dock_stage_t;

typedef struct {
    dock_stage_t stage;
    float timer_s;
    float start_encoder_dist_m;
    float target_exit_dist_m;
    float exit_velocity_mps;
    bool is_marine;
} dock_procedure_t;

void dock_procedure_init(dock_procedure_t *proc, bool is_marine, float exit_dist_m, float exit_vel_mps) {
    proc->stage = DOCK_STAGE_IDLE;
    proc->timer_s = 0.0f;
    proc->start_encoder_dist_m = 0.0f;
    proc->target_exit_dist_m = exit_dist_m;
    proc->exit_velocity_mps = exit_vel_mps;
    proc->is_marine = is_marine;
}

void dock_procedure_update(dock_procedure_t *proc,
                           float dt,
                           float charge_current_a,
                           float pitch_rad,
                           float mass_kg,
                           float wheel_radius_m,
                           float gear_ratio,
                           float encoder_dist_m,
                           float current_left_a,
                           float current_right_a,
                           float gnss_speed_mps,
                           float *out_linear_vel,
                           float *out_angular_vel,
                           float *out_pre_torque_nm,
                           bool *out_brake_release)
{
    proc->timer_s += dt;
    *out_linear_vel = 0.0f;
    *out_angular_vel = 0.0f;
    *out_pre_torque_nm = 0.0f;
    *out_brake_release = false;

    switch (proc->stage) {
        case DOCK_STAGE_IDLE:
            break;

        case DOCK_STAGE_CHECK_POWER:
            // Валідація відсутності зарядного струму (зняття живлення реле)
            if (fabsf(charge_current_a) < 0.05f) {
                proc->stage = proc->is_marine ? DOCK_STAGE_UNMOORING_BURST : DOCK_STAGE_PRE_TORQUE;
                proc->timer_s = 0.0f;
            } else if (proc->timer_s > 3.0f) {
                proc->stage = DOCK_STAGE_ABORT_FAULT; // Збій розмикання контактів
            }
            break;

        case DOCK_STAGE_PRE_TORQUE: {
            // Розрахунок моменту компенсації сили тяжіння на схилі: M = (m*g*sin(pitch)*r)/(2*i)
            float g = 9.80665f;
            float m_hold = (mass_kg * g * sinf(pitch_rad) * wheel_radius_m) / (2.0f * gear_ratio);
            *out_pre_torque_nm = m_hold;

            if (proc->timer_s > 0.2f) {
                *out_brake_release = true; // Зняття гальма після виходу на опорний момент
            }
            if (proc->timer_s > 0.6f) {
                proc->stage = DOCK_STAGE_REVERSE_CORRIDOR;
                proc->timer_s = 0.0f;
                proc->start_encoder_dist_m = encoder_dist_m;
            }
            break;
        }

        case DOCK_STAGE_REVERSE_CORRIDOR: {
            *out_brake_release = true;
            *out_linear_vel = -fabsf(proc->exit_velocity_mps); // Реверс
            *out_angular_vel = 0.0f; // Рух суворо вздовж осі

            // Захист від заклинювання в напрямних за струмом двигунів
            if (fabsf(current_left_a) > 20.0f || fabsf(current_right_a) > 20.0f) {
                proc->stage = DOCK_STAGE_ABORT_FAULT;
                break;
            }

            float s_traveled = fabsf(encoder_dist_m - proc->start_encoder_dist_m);
            if (s_traveled >= proc->target_exit_dist_m) {
                proc->stage = DOCK_STAGE_TRACTION_VALIDATE;
                proc->timer_s = 0.0f;
            } else if (proc->timer_s > 15.0f) {
                proc->stage = DOCK_STAGE_ABORT_FAULT; // Таймаут реверсу
            }
            break;
        }

        case DOCK_STAGE_UNMOORING_BURST:
            // Для човна: короткий імпульс розвороту носа від причалу
            *out_angular_vel = 0.45f;
            *out_linear_vel = -0.30f;
            if (proc->timer_s > 1.2f) {
                proc->stage = DOCK_STAGE_HEADING_ALIGN;
                proc->timer_s = 0.0f;
            }
            break;

        case DOCK_STAGE_TRACTION_VALIDATE:
            *out_brake_release = true;
            *out_linear_vel = -proc->exit_velocity_mps * 0.5f;
            if (proc->timer_s > 1.0f) {
                proc->stage = DOCK_STAGE_HEADING_ALIGN;
                proc->timer_s = 0.0f;
            }
            break;

        case DOCK_STAGE_HEADING_ALIGN:
            *out_brake_release = true;
            *out_linear_vel = proc->exit_velocity_mps;
            // Успішний вихід при наборі швидкості для GNSS COG або за таймаутом
            if (gnss_speed_mps > 0.8f || proc->timer_s > 4.0f) {
                proc->stage = DOCK_STAGE_SUCCESS;
            }
            break;

        case DOCK_STAGE_SUCCESS:
            *out_brake_release = true;
            break;

        case DOCK_STAGE_ABORT_FAULT:
            *out_brake_release = false; // Аварійне затискання гальм
            *out_linear_vel = 0.0f;
            *out_angular_vel = 0.0f;
            break;
    }
}
