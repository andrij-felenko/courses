#include <stdint.h>
#include <stdbool.h>
#include <math.h>

// Перелік станів автомата виходу з дока
typedef enum {
    DOCK_FSM_IDLE = 0,
    DOCK_FSM_POWER_CHECK,
    DOCK_FSM_PRE_TORQUE,
    DOCK_FSM_CORRIDOR_REVERSE,
    DOCK_FSM_UNMOORING_BURST,
    DOCK_FSM_TRACTION_CHECK,
    DOCK_FSM_HEADING_ALIGN,
    DOCK_FSM_COMPLETE,
    DOCK_FSM_ABORT
} dock_fsm_state_t;

// Коди помилок автомата
typedef enum {
    DOCK_ERR_NONE = 0,
    DOCK_ERR_POWER_NOT_DISCONNECTED,
    DOCK_ERR_BRAKE_RELEASE_FAILED,
    DOCK_ERR_CORRIDOR_JAMMED,
    DOCK_ERR_EXCESSIVE_SLIP,
    DOCK_ERR_TIMEOUT
} dock_fsm_error_t;

// Конфігураційні параметри процедури
typedef struct {
    bool is_marine_vehicle;      // true = USV (човен), false = UGV (ровер)
    float exit_velocity_mps;     // Швидкість реверсу у коридорі (м/с)
    float exit_distance_m;       // Довжина напрямних дока (м)
    float vehicle_mass_kg;       // Маса платформи (кг)
    float wheel_radius_m;        // Радіус колеса (м)
    float gear_ratio;            // Передатне число редуктора
    float max_allowed_slip;      // Граничний коефіцієнт ковзання (напр. 0.25)
    float max_motor_current_a;   // Струм відсічки при заклинюванні (А)
    float unmooring_burst_thrust;// Амплітуда імпульсу відчалювання (0.0..1.0)
    float unmooring_burst_dur_s; // Тривалість імпульсу відчалювання (с)
    float phase_timeout_s;       // Таймаут на окрему фазу (с)
} dock_fsm_config_t;

// Вхідні дані телеметрії сенсорів
typedef struct {
    float charge_current_a;      // Струм зарядної лінії
    float dock_voltage_v;        // Напруга на контактах
    float pitch_angle_rad;       // Тангаж (кут схилу)
    float current_left_a;        // Струм лівого мотора
    float current_right_a;       // Струм правого мотора
    float encoder_dist_m;        // Пройдена дистанція за енкодерами
    float encoder_vel_mps;       // Лінійна швидкість за енкодерами
    float imu_accel_x_mps2;      // Поздовжнє прискорення з IMU
    float imu_gyro_z_radps;      // Кутова швидкість рискання
    float gnss_ground_speed_mps; // Швидкість за GNSS
} dock_fsm_inputs_t;

// Вихідні команди на приводи
typedef struct {
    float cmd_vel_linear_mps;    // Задана лінійна швидкість
    float cmd_vel_angular_radps; // Задана кутова швидкість
    float cmd_motor_torque_nm;   // Момент утримання (Pre-Torque)
    float cmd_thrust_left;       // Тяга лівого рушія (-1.0..1.0)
    float cmd_thrust_right;      // Тяга правого рушія (-1.0..1.0)
    bool brake_release_gpio;     // Сигнал зняття стоянкового гальма
} dock_fsm_outputs_t;

// Контекст автомата
typedef struct {
    dock_fsm_state_t state;
    dock_fsm_error_t error;
    dock_fsm_config_t cfg;
    float state_timer_s;
    float start_encoder_dist_m;
    float integrated_heading_rad;
} dock_fsm_context_t;

void dock_fsm_init(dock_fsm_context_t *ctx, const dock_fsm_config_t *cfg) {
    ctx->state = DOCK_FSM_IDLE;
    ctx->error = DOCK_ERR_NONE;
    ctx->cfg = *cfg;
    ctx->state_timer_s = 0.0f;
    ctx->start_encoder_dist_m = 0.0f;
    ctx->integrated_heading_rad = 0.0f;
}

void dock_fsm_start(dock_fsm_context_t *ctx) {
    if (ctx->state == DOCK_FSM_IDLE) {
        ctx->state = DOCK_FSM_POWER_CHECK;
        ctx->error = DOCK_ERR_NONE;
        ctx->state_timer_s = 0.0f;
    }
}

void dock_fsm_step(dock_fsm_context_t *ctx, 
                   const dock_fsm_inputs_t *in, 
                   dock_fsm_outputs_t *out, 
                   float dt) 
{
    ctx->state_timer_s += dt;
    ctx->integrated_heading_rad += in->imu_gyro_z_radps * dt;

    // Скидання вихідних команд за замовчуванням
    out->cmd_vel_linear_mps = 0.0f;
    out->cmd_vel_angular_radps = 0.0f;
    out->cmd_motor_torque_nm = 0.0f;
    out->cmd_thrust_left = 0.0f;
    out->cmd_thrust_right = 0.0f;
    out->brake_release_gpio = false;

    switch (ctx->state) {
        case DOCK_FSM_IDLE:
            break;

        case DOCK_FSM_POWER_CHECK:
            // Перевірка фізичного розриву ланцюга заряду
            if (fabsf(in->charge_current_a) < 0.05f && in->dock_voltage_v < 1.5f) {
                if (ctx->cfg.is_marine_vehicle) {
                    ctx->state = DOCK_FSM_UNMOORING_BURST;
                } else {
                    ctx->state = DOCK_FSM_PRE_TORQUE;
                }
                ctx->state_timer_s = 0.0f;
            } else if (ctx->state_timer_s > ctx->cfg.phase_timeout_s) {
                ctx->state = DOCK_FSM_ABORT;
                ctx->error = DOCK_ERR_POWER_NOT_DISCONNECTED;
            }
            break;

        case DOCK_FSM_PRE_TORQUE: {
            // Розрахунок антискочувального моменту для ровера: M = (m * g * sin(pitch) * r) / (2 * i)
            float g = 9.80665f;
            float slope_torque = (ctx->cfg.vehicle_mass_kg * g * sinf(in->pitch_angle_rad) * 
                                  ctx->cfg.wheel_radius_m) / (2.0f * ctx->cfg.gear_ratio);
            
            out->cmd_motor_torque_nm = slope_torque;
            
            // Після 200 мс натягу трансмісії подаємо сигнал на розтискання колодок
            if (ctx->state_timer_s > 0.2f) {
                out->brake_release_gpio = true;
            }

            if (ctx->state_timer_s > 0.6f) {
                ctx->state = DOCK_FSM_CORRIDOR_REVERSE;
                ctx->state_timer_s = 0.0f;
                ctx->start_encoder_dist_m = in->encoder_dist_m;
            }
            break;
        }

        case DOCK_FSM_CORRIDOR_REVERSE: {
            out->brake_release_gpio = true;
            out->cmd_vel_linear_mps = -fabsf(ctx->cfg.exit_velocity_mps); // Реверс
            out->cmd_vel_angular_radps = 0.0f; // Суворо прямо

            // Захист від механічного заклинювання в напрямних
            if (fabsf(in->current_left_a) > ctx->cfg.max_motor_current_a ||
                fabsf(in->current_right_a) > ctx->cfg.max_motor_current_a) {
                ctx->state = DOCK_FSM_ABORT;
                ctx->error = DOCK_ERR_CORRIDOR_JAMMED;
                break;
            }

            float traveled = fabsf(in->encoder_dist_m - ctx->start_encoder_dist_m);
            if (traveled >= ctx->cfg.exit_distance_m) {
                ctx->state = DOCK_FSM_TRACTION_CHECK;
                ctx->state_timer_s = 0.0f;
            } else if (ctx->state_timer_s > ctx->cfg.phase_timeout_s) {
                ctx->state = DOCK_FSM_ABORT;
                ctx->error = DOCK_ERR_TIMEOUT;
            }
            break;
        }

        case DOCK_FSM_UNMOORING_BURST:
            // Сплеск різнотягу для відтискання носа катера від причалу
            out->cmd_thrust_left = ctx->cfg.unmooring_burst_thrust;
            out->cmd_thrust_right = -ctx->cfg.unmooring_burst_thrust * 0.5f;

            if (ctx->state_timer_s >= ctx->cfg.unmooring_burst_dur_s) {
                ctx->state = DOCK_FSM_HEADING_ALIGN;
                ctx->state_timer_s = 0.0f;
            }
            break;

        case DOCK_FSM_TRACTION_CHECK: {
            out->brake_release_gpio = true;
            out->cmd_vel_linear_mps = -ctx->cfg.exit_velocity_mps * 0.5f;

            // Оцінка пробуксовки: порівняння швидкості енкодерів з інтегрованим прискоренням
            float est_speed = fabsf(in->imu_accel_x_mps2 * ctx->state_timer_s);
            float enc_speed = fabsf(in->encoder_vel_mps);
            float max_s = enc_speed > est_speed ? enc_speed : est_speed;
            
            float slip_ratio = 0.0f;
            if (max_s > 0.05f) {
                slip_ratio = fabsf(enc_speed - est_speed) / max_s;
            }

            if (slip_ratio > ctx->cfg.max_allowed_slip && ctx->state_timer_s > 0.5f) {
                ctx->state = DOCK_FSM_ABORT;
                ctx->error = DOCK_ERR_EXCESSIVE_SLIP;
            } else if (ctx->state_timer_s > 1.0f) {
                ctx->state = DOCK_FSM_HEADING_ALIGN;
                ctx->state_timer_s = 0.0f;
            }
            break;
        }

        case DOCK_FSM_HEADING_ALIGN:
            out->brake_release_gpio = true;
            // Утримання нульового кутового відхилення від осі виходу
            out->cmd_vel_angular_radps = -1.5f * ctx->integrated_heading_rad;
            out->cmd_vel_linear_mps = ctx->cfg.exit_velocity_mps;

            // Критерій успіху: набір швидкості для валідації курсу GNSS
            if (in->gnss_ground_speed_mps > 0.8f || ctx->state_timer_s > 3.0f) {
                ctx->state = DOCK_FSM_COMPLETE;
            }
            break;

        case DOCK_FSM_COMPLETE:
            out->brake_release_gpio = true;
            break;

        case DOCK_FSM_ABORT:
            // Аварійний скид: мотори блокуються, гальмо затискається
            out->brake_release_gpio = false;
            out->cmd_vel_linear_mps = 0.0f;
            out->cmd_vel_angular_radps = 0.0f;
            break;
    }
}
