#include <stdint.h>
#include <stdbool.h>
#include <math.h>

typedef enum {
    RTL_STATE_IDLE = 0,
    RTL_STATE_CLIMB,             // Фаза 1: Вертикальний набір безпечної висоти
    RTL_STATE_RETURN_TRANSIT,    // Фаза 2: Крейсерський рух до бази (Direct/Reverse)
    RTL_STATE_HOVER_ALIGN,       // Фаза 3: Зависання над точкою та пошук мітки
    RTL_STATE_PRECISION_DESCENT, // Фаза 4: Оптичне зниження з контролем конуса
    RTL_STATE_TOUCHDOWN_WAIT,    // Фаза 5: Детектування землі та відлік таймауту
    RTL_STATE_COMPLETED          // Фінал: Мотори зупинено (Disarmed)
} rtl_state_t;

typedef struct {
    float x, y, z;               // Координати в локальній системі NED (метри)
    float vx, vy, vz;            // Швидкості NED (м/с)
} nav_pose_t;

typedef struct {
    float x, y, z;               // Зміщення мітки в системі NED відносно дрона
    bool  is_detected;           // Прапорець достовірності візуального контакту
} optical_target_t;

typedef struct {
    float rtl_altitude_min;      // Мінімальна безпечна висота повернення (м)
    float cruise_speed_xy;       // Крейсерська горизонтальна швидкість (м/с)
    float climb_rate_z;          // Швидкість підйому (м/с)
    float descent_rate_fast;     // Швидкість швидкого зниження (м/с)
    float descent_rate_slow;     // Швидкість фінального підкрадання (м/с)
    float max_tilt_angle_rad;    // Граничний кут нахилу проти вітру (рад)
    float home_reach_radius;     // Радіус прийняття виходу в домашню точку (м)
} rtl_config_t;

typedef struct {
    rtl_state_t   state;
    rtl_config_t  cfg;
    nav_pose_t    home_pose;
    float         target_cruise_alt;
    uint32_t      ground_contact_start_ms;
    bool          disarm_commanded;
} rtl_controller_t;

void rtl_init(rtl_controller_t *rtl, const rtl_config_t *cfg, const nav_pose_t *home) {
    rtl->state = RTL_STATE_IDLE;
    rtl->cfg = *cfg;
    rtl->home_pose = *home;
    rtl->target_cruise_alt = cfg->rtl_altitude_min;
    rtl->ground_contact_start_ms = 0;
    rtl->disarm_commanded = false;
}

void rtl_start(rtl_controller_t *rtl, const nav_pose_t *current) {
    // Якщо поточна висота більша за мінімальну безпечну — тримаємо поточну
    if (current->z > rtl->cfg.rtl_altitude_min) {
        rtl->target_cruise_alt = current->z;
    } else {
        rtl->target_cruise_alt = rtl->cfg.rtl_altitude_min;
    }
    rtl->state = RTL_STATE_CLIMB;
    rtl->ground_contact_start_ms = 0;
    rtl->disarm_commanded = false;
}

// Виклик у періодичному циклі навігатора (50 Гц)
void rtl_update(rtl_controller_t *rtl, const nav_pose_t *cur, 
                const optical_target_t *opt, float throttle_out,
                uint32_t now_ms, nav_pose_t *cmd_out) {
    
    switch (rtl->state) {
        case RTL_STATE_CLIMB: {
            // Утримуємо поточні X, Y на місці, набираємо безпечний ешелон
            cmd_out->x = cur->x;
            cmd_out->y = cur->y;
            cmd_out->z = rtl->target_cruise_alt;
            cmd_out->vz = rtl->cfg.climb_rate_z;
            cmd_out->vx = 0.0f;
            cmd_out->vy = 0.0f;

            if (cur->z >= (rtl->target_cruise_alt - 0.5f)) {
                rtl->state = RTL_STATE_RETURN_TRANSIT;
            }
            break;
        }

        case RTL_STATE_RETURN_TRANSIT: {
            // Рух до домашньої точки на зафіксованій маршовій висоті
            float dx = rtl->home_pose.x - cur->x;
            float dy = rtl->home_pose.y - cur->y;
            float dist = sqrtf(dx * dx + dy * dy);

            cmd_out->x = rtl->home_pose.x;
            cmd_out->y = rtl->home_pose.y;
            cmd_out->z = rtl->target_cruise_alt;
            cmd_out->vz = 0.0f;

            if (dist > rtl->cfg.home_reach_radius) {
                cmd_out->vx = (dx / dist) * rtl->cfg.cruise_speed_xy;
                cmd_out->vy = (dy / dist) * rtl->cfg.cruise_speed_xy;
            } else {
                // Вийшли в зону бази — переходимо до зависання й оптичного пошуку
                cmd_out->vx = 0.0f;
                cmd_out->vy = 0.0f;
                rtl->state = RTL_STATE_HOVER_ALIGN;
            }
            break;
        }

        case RTL_STATE_HOVER_ALIGN: {
            cmd_out->x = rtl->home_pose.x;
            cmd_out->y = rtl->home_pose.y;
            cmd_out->z = rtl->target_cruise_alt;
            cmd_out->vx = 0.0f;
            cmd_out->vy = 0.0f;
            cmd_out->vz = 0.0f;

            // Якщо оптичний маркер знайдено або вийшов таймаут очікування — починаємо спуск
            rtl->state = RTL_STATE_PRECISION_DESCENT;
            break;
        }

        case RTL_STATE_PRECISION_DESCENT: {
            // Дворівневий профіль зниження
            float vz_target = (cur->z > 5.0f) ? -rtl->cfg.descent_rate_fast 
                                              : -rtl->cfg.descent_rate_slow;

            if (opt->is_detected) {
                // Оптична корекція горизонтальної позиції
                float kp_opt = 0.8f;
                cmd_out->vx = -kp_opt * opt->x;
                cmd_out->vy = -kp_opt * opt->y;

                // Захист: якщо дрейф завеликий — зависаємо, доки не відцентруємось
                float opt_offset = sqrtf(opt->x * opt->x + opt->y * opt->y);
                if (opt_offset > (cur->z * 0.3f) && cur->z > 1.5f) {
                    vz_target = 0.0f; // Призупинити зниження
                }
            } else {
                // Без оптики тримаємо GNSS координати бази
                cmd_out->x = rtl->home_pose.x;
                cmd_out->y = rtl->home_pose.y;
                cmd_out->vx = 0.0f;
                cmd_out->vy = 0.0f;
            }

            cmd_out->z = 0.0f; // Ціль — земля
            cmd_out->vz = vz_target;

            // Критерій входу в стан торкання (вертикальна швидкість біля 0 і низький газ)
            if (cur->z < 1.0f && fabsf(cur->vz) < 0.15f && throttle_out < 0.25f) {
                rtl->state = RTL_STATE_TOUCHDOWN_WAIT;
                rtl->ground_contact_start_ms = now_ms;
            }
            break;
        }

        case RTL_STATE_TOUCHDOWN_WAIT: {
            cmd_out->vx = 0.0f;
            cmd_out->vy = 0.0f;
            cmd_out->vz = -0.2f; // Притискаємо до землі на мінімальних обертах

            // Перевіряємо стійкість контакту протягом 1.2 секунди
            if (fabsf(cur->vz) < 0.15f && throttle_out < 0.25f) {
                if ((now_ms - rtl->ground_contact_start_ms) > 1200u) {
                    rtl->disarm_commanded = true;
                    rtl->state = RTL_STATE_COMPLETED;
                }
            } else {
                // Хибне спрацювання (підстрибнув) — повертаємося до фінального спуску
                rtl->state = RTL_STATE_PRECISION_DESCENT;
            }
            break;
        }

        case RTL_STATE_COMPLETED:
        case RTL_STATE_IDLE:
        default:
            cmd_out->vx = 0.0f;
            cmd_out->vy = 0.0f;
            cmd_out->vz = 0.0f;
            break;
    }
}
