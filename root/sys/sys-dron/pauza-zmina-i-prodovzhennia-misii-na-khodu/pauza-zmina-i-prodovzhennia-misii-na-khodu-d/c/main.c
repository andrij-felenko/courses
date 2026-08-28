#include <stdbool.h>
#include <stdint.h>
#include <math.h>
#include <string.h>

#define MISSION_MAX_WAYPOINTS 64

typedef enum {
    DYN_STATE_IDLE = 0,
    DYN_STATE_NAVIGATING,
    DYN_STATE_PAUSED_HOLD,
    DYN_STATE_REJOINING,
    DYN_STATE_COMPLETED
} DynState;

typedef struct {
    double x_ned;           /* Позиція North, метри від Home */
    double y_ned;           /* Позиція East, метри від Home */
    float z_ned;            /* Позиція Down, метри від Home (від'ємна висота) */
    float acceptance_rad_m; /* Радіус досягнення точки */
    float cruise_speed_mps; /* Швидкість на сегменті */
    uint16_t action_id;     /* Команда дії */
} WaypointNed;

typedef struct {
    WaypointNed items[MISSION_MAX_WAYPOINTS];
    uint16_t count;
    uint32_t version;
} MissionStorage;

typedef struct {
    MissionStorage buffers[2];
    volatile uint8_t active_idx;
    volatile uint32_t seqlock;

    DynState state;
    uint16_t current_seq;

    /* Зріз контексту паузи */
    double hold_x;
    double hold_y;
    float hold_z;
    double proj_x;
    double proj_y;
    float remaining_dist;

    /* Налаштування динаміки */
    float max_intercept_rad;
    float lookahead_time_s;
} DynamicMissionEngine;

void dyn_engine_init(DynamicMissionEngine *eng) {
    memset(eng, 0, sizeof(*eng));
    eng->state = DYN_STATE_IDLE;
    eng->max_intercept_rad = 35.0f * (3.14159265f / 180.0f);
    eng->lookahead_time_s = 3.0f;
}

/* Перехід у режим паузи */
bool dyn_engine_pause(DynamicMissionEngine *eng, double cur_x, double cur_y, float cur_z) {
    if (eng->state != DYN_STATE_NAVIGATING && eng->state != DYN_STATE_REJOINING) {
        return false;
    }

    eng->hold_x = cur_x;
    eng->hold_y = cur_y;
    eng->hold_z = cur_z;
    eng->state = DYN_STATE_PAUSED_HOLD;
    return true;
}

/* Атомарна заміна невиконаного хвоста маршруту */
bool dyn_engine_replace_tail(DynamicMissionEngine *eng,
                             uint16_t start_seq,
                             const WaypointNed *new_items,
                             uint16_t new_count) {
    /* Не дозволяємо змінювати точку, яка вже виконується, якщо не в режимі паузи */
    if (eng->state == DYN_STATE_NAVIGATING && start_seq <= eng->current_seq) {
        return false;
    }
    if ((start_seq + new_count) > MISSION_MAX_WAYPOINTS) {
        return false;
    }

    uint8_t staging_idx = 1 - eng->active_idx;
    MissionStorage *staging = &eng->buffers[staging_idx];
    const MissionStorage *active = &eng->buffers[eng->active_idx];

    /* Зберігаємо історію до точки розгалуження */
    if (start_seq > 0) {
        memcpy(staging->items, active->items, sizeof(WaypointNed) * start_seq);
    }
    /* Записуємо новий хвіст */
    memcpy(&staging->items[start_seq], new_items, sizeof(WaypointNed) * new_count);
    staging->count = start_seq + new_count;
    staging->version = active->version + 1;

    /* Атомарний swap через SeqLock */
    eng->seqlock++;
    __sync_synchronize();
    eng->active_idx = staging_idx;
    __sync_synchronize();
    eng->seqlock++;

    return true;
}

/* Відновлення виконання місії */
bool dyn_engine_resume(DynamicMissionEngine *eng) {
    if (eng->state != DYN_STATE_PAUSED_HOLD) {
        return false;
    }
    eng->state = DYN_STATE_REJOINING;
    return true;
}

/* Розрахунок навігаційних уставок у циклі керування 50 Гц */
void dyn_engine_update(DynamicMissionEngine *eng,
                       double cur_x, double cur_y, float cur_z,
                       float out_vel_ned[3], float *out_yaw_rad) {
    if (eng->state == DYN_STATE_PAUSED_HOLD) {
        out_vel_ned[0] = 0.0f;
        out_vel_ned[1] = 0.0f;
        out_vel_ned[2] = 0.0f;
        return;
    }

    const MissionStorage *buf = &eng->buffers[eng->active_idx];
    if (eng->current_seq >= buf->count) {
        eng->state = DYN_STATE_COMPLETED;
        out_vel_ned[0] = 0.0f;
        out_vel_ned[1] = 0.0f;
        out_vel_ned[2] = 0.0f;
        return;
    }

    const WaypointNed *curr_wp = &buf->items[eng->current_seq];
    double dx = curr_wp->x_ned - cur_x;
    double dy = curr_wp->y_ned - cur_y;
    double dist = sqrt(dx * dx + dy * dy);

    /* Перевірка досягнення точки */
    if (dist <= (double)curr_wp->acceptance_rad_m) {
        eng->current_seq++;
        if (eng->current_seq >= buf->count) {
            eng->state = DYN_STATE_COMPLETED;
            out_vel_ned[0] = 0.0f;
            out_vel_ned[1] = 0.0f;
            out_vel_ned[2] = 0.0f;
            return;
        }
    }

    /* Наведення та обмеження кута зближення */
    float cruise = curr_wp->cruise_speed_mps > 1.0f ? curr_wp->cruise_speed_mps : 12.0f;
    float track_yaw = (float)atan2(dy, dx);

    out_vel_ned[0] = (float)cos(track_yaw) * cruise;
    out_vel_ned[1] = (float)sin(track_yaw) * cruise;
    out_vel_ned[2] = 0.0f;
    *out_yaw_rad = track_yaw;
}
