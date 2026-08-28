#include <stdint.h>
#include <stdbool.h>
#include <math.h>
#include <string.h>

#define RTL_MAX_BREADCRUMBS        64u
#define RTL_BREADCRUMB_MIN_DIST_M  8.0f
#define RTL_BREADCRUMB_PRUNE_EPS_M 1.5f
#define RTL_GROUND_DET_TIMEOUT_MS  1200u

typedef enum {
    FSM_IDLE = 0,
    FSM_CLIMB_SAFE_ALT,         // Вертикальний підйом на безпечний ешелон
    FSM_REVERSE_PATH_TRANSIT,   // Відкат за записаними крихтами назад
    FSM_DIRECT_HOME_TRANSIT,    // Прямий доліт до домашньої точки
    FSM_HOVER_SEARCH_TARGET,    // Зависання та оптичний пошук мітки
    FSM_PRECISION_DESCENT,      // Керований спуск із візуальним центруванням
    FSM_GROUND_WAIT_DISARM,     // Детектування землі та відлік таймауту
    FSM_DISARMED_DONE           // Мотори знеструмлено, завершення
} rtl_fsm_state_t;

typedef struct {
    float x, y, z;               // Координати в системі NED (метри)
    float vx, vy, vz;            // Швидкості NED (м/с)
} point3d_t;

typedef struct {
    float x, y, z;               // Зміщення мітки відносно дрона в NED (м)
    bool  valid;                 // Ознака достовірного розпізнавання
} vision_target_t;

typedef struct {
    point3d_t buffer[RTL_MAX_BREADCRUMBS];
    uint16_t  head;
    uint16_t  count;
} breadcrumb_ring_t;

typedef struct {
    float min_rtl_alt_m;         // Мінімальна висота безпечного ешелону (м)
    float cruise_speed_ms;       // Швидкість горизонтального транзиту (м/с)
    float climb_speed_ms;        // Вертикальна швидкість підйому (м/с)
    float descent_fast_ms;       // Швидкість швидкого зниження (м/с)
    float descent_slow_ms;       // Швидкість фінальної посадки (м/с)
    float accept_radius_m;       // Радіус досягнення точки маршруту (м)
    float optical_kp;            // Коефіцієнт оптичного центрування
} rtl_params_t;

typedef struct {
    rtl_fsm_state_t   state;
    rtl_params_t      params;
    breadcrumb_ring_t crumbs;
    point3d_t         home_point;
    float             active_cruise_alt_m;
    int16_t           crumb_reverse_idx;
    uint32_t          ground_timer_start_ms;
    bool              disarm_signal;
} rtl_engine_t;

// Ініціалізація кільцевого буфера
void crumbs_init(breadcrumb_ring_t *b) {
    b->head = 0;
    b->count = 0;
    memset(b->buffer, 0, sizeof(b->buffer));
}

// Додавання нової точки з перевіркою мінімальної дистанції
void crumbs_push(breadcrumb_ring_t *b, const point3d_t *p) {
    if (b->count > 0) {
        uint16_t last_idx = (b->head == 0) ? (RTL_MAX_BREADCRUMBS - 1) : (b->head - 1);
        float dx = p->x - b->buffer[last_idx].x;
        float dy = p->y - b->buffer[last_idx].y;
        float dz = p->z - b->buffer[last_idx].z;
        float dist_sq = dx * dx + dy * dy + dz * dz;

        if (dist_sq < (RTL_BREADCRUMB_MIN_DIST_M * RTL_BREADCRUMB_MIN_DIST_M)) {
            return; // Занадто близько до попередньої точки — пропускаємо
        }
    }

    b->buffer[b->head] = *p;
    b->head = (b->head + 1) % RTL_MAX_BREADCRUMBS;
    if (b->count < RTL_MAX_BREADCRUMBS) {
        b->count++;
    }
}

// Ініціалізація модуля RTL
void rtl_engine_init(rtl_engine_t *eng, const rtl_params_t *params, const point3d_t *home) {
    eng->state = FSM_IDLE;
    eng->params = *params;
    eng->home_point = *home;
    eng->active_cruise_alt_m = params->min_rtl_alt_m;
    eng->crumb_reverse_idx = -1;
    eng->ground_timer_start_ms = 0;
    eng->disarm_signal = false;
    crumbs_init(&eng->crumbs);
}

// Запуск процедури повернення
void rtl_engine_trigger(rtl_engine_t *eng, const point3d_t *current) {
    float cur_alt = -current->z; // У системі NED висота h = -Z
    if (cur_alt > eng->params.min_rtl_alt_m) {
        eng->active_cruise_alt_m = cur_alt;
    } else {
        eng->active_cruise_alt_m = eng->params.min_rtl_alt_m;
    }

    eng->crumb_reverse_idx = (int16_t)eng->crumbs.count - 1;
    eng->state = FSM_CLIMB_SAFE_ALT;
    eng->ground_timer_start_ms = 0;
    eng->disarm_signal = false;
}

// Головний ітераційний крок автомата (50 Гц)
void rtl_engine_step(rtl_engine_t *eng, const point3d_t *cur,
                     const vision_target_t *vision, float throttle_ratio,
                     uint32_t now_ms, point3d_t *setpoint_out) {

    switch (eng->state) {
        case FSM_CLIMB_SAFE_ALT: {
            // Вертикальний підйом на місці
            setpoint_out->x = cur->x;
            setpoint_out->y = cur->y;
            setpoint_out->z = -eng->active_cruise_alt_m;
            setpoint_out->vx = 0.0f;
            setpoint_out->vy = 0.0f;
            setpoint_out->vz = -eng->params.climb_speed_ms;

            if ((-cur->z) >= (eng->active_cruise_alt_m - 0.5f)) {
                // Якщо є крихти маршруту — йдемо за ними, інакше напряму до бази
                if (eng->crumb_reverse_idx >= 0) {
                    eng->state = FSM_REVERSE_PATH_TRANSIT;
                } else {
                    eng->state = FSM_DIRECT_HOME_TRANSIT;
                }
            }
            break;
        }

        case FSM_REVERSE_PATH_TRANSIT: {
            if (eng->crumb_reverse_idx < 0) {
                eng->state = FSM_DIRECT_HOME_TRANSIT;
                break;
            }

            point3d_t target_wp = eng->crumbs.buffer[eng->crumb_reverse_idx];
            float dx = target_wp.x - cur->x;
            float dy = target_wp.y - cur->y;
            float dist = sqrtf(dx * dx + dy * dy);

            setpoint_out->x = target_wp.x;
            setpoint_out->y = target_wp.y;
            setpoint_out->z = -eng->active_cruise_alt_m;
            setpoint_out->vz = 0.0f;

            if (dist > eng->params.accept_radius_m) {
                setpoint_out->vx = (dx / dist) * eng->params.cruise_speed_ms;
                setpoint_out->vy = (dy / dist) * eng->params.cruise_speed_ms;
            } else {
                // Досягли проміжної точки — беремо попередню
                eng->crumb_reverse_idx--;
                if (eng->crumb_reverse_idx < 0) {
                    eng->state = FSM_DIRECT_HOME_TRANSIT;
                }
            }
            break;
        }

        case FSM_DIRECT_HOME_TRANSIT: {
            float dx = eng->home_point.x - cur->x;
            float dy = eng->home_point.y - cur->y;
            float dist = sqrtf(dx * dx + dy * dy);

            setpoint_out->x = eng->home_point.x;
            setpoint_out->y = eng->home_point.y;
            setpoint_out->z = -eng->active_cruise_alt_m;
            setpoint_out->vz = 0.0f;

            if (dist > eng->params.accept_radius_m) {
                setpoint_out->vx = (dx / dist) * eng->params.cruise_speed_ms;
                setpoint_out->vy = (dy / dist) * eng->params.cruise_speed_ms;
            } else {
                setpoint_out->vx = 0.0f;
                setpoint_out->vy = 0.0f;
                eng->state = FSM_HOVER_SEARCH_TARGET;
            }
            break;
        }

        case FSM_HOVER_SEARCH_TARGET: {
            setpoint_out->x = eng->home_point.x;
            setpoint_out->y = eng->home_point.y;
            setpoint_out->z = -eng->active_cruise_alt_m;
            setpoint_out->vx = 0.0f;
            setpoint_out->vy = 0.0f;
            setpoint_out->vz = 0.0f;

            eng->state = FSM_PRECISION_DESCENT;
            break;
        }

        case FSM_PRECISION_DESCENT: {
            float cur_alt = -cur->z;
            float vz_desc = (cur_alt > 5.0f) ? eng->params.descent_fast_ms 
                                             : eng->params.descent_slow_ms;

            if (vision->valid) {
                // Візуальне пропорційне наведення на мітку
                setpoint_out->vx = -eng->params.optical_kp * vision->x;
                setpoint_out->vy = -eng->params.optical_kp * vision->y;

                float offset = sqrtf(vision->x * vision->x + vision->y * vision->y);
                // Якщо похибка виходить за межі конуса — зупиняємо спуск
                if (offset > (cur_alt * 0.35f) && cur_alt > 1.2f) {
                    vz_desc = 0.0f;
                }
            } else {
                setpoint_out->x = eng->home_point.x;
                setpoint_out->y = eng->home_point.y;
                setpoint_out->vx = 0.0f;
                setpoint_out->vy = 0.0f;
            }

            setpoint_out->z = 0.0f;
            setpoint_out->vz = vz_desc;

            // Критерій торкання землі: низька висота, близька до нуля швидкість, низький газ
            if (cur_alt < 0.8f && fabsf(cur->vz) < 0.12f && throttle_ratio < 0.20f) {
                eng->state = FSM_GROUND_WAIT_DISARM;
                eng->ground_timer_start_ms = now_ms;
            }
            break;
        }

        case FSM_GROUND_WAIT_DISARM: {
            setpoint_out->vx = 0.0f;
            setpoint_out->vy = 0.0f;
            setpoint_out->vz = 0.15f; // Легкий притиск до ґрунту

            if (fabsf(cur->vz) < 0.12f && throttle_ratio < 0.20f) {
                if ((now_ms - eng->ground_timer_start_ms) >= RTL_GROUND_DET_TIMEOUT_MS) {
                    eng->disarm_signal = true;
                    eng->state = FSM_DISARMED_DONE;
                }
            } else {
                // Підстрибування або порив вітру — повернення до посадки
                eng->state = FSM_PRECISION_DESCENT;
            }
            break;
        }

        case FSM_DISARMED_DONE:
        case FSM_IDLE:
        default:
            setpoint_out->vx = 0.0f;
            setpoint_out->vy = 0.0f;
            setpoint_out->vz = 0.0f;
            break;
    }
}
