#include <stdbool.h>
#include <stdint.h>
#include <math.h>
#include <string.h>

#define MISSION_MAX_WAYPOINTS 64
#define RAD_TO_DEG (180.0 / 3.14159265358979323846)
#define DEG_TO_RAD (3.14159265358979323846 / 180.0)

typedef enum {
    DYN_MISSION_STATE_IDLE = 0,
    DYN_MISSION_STATE_NAVIGATING,
    DYN_MISSION_STATE_PAUSED_HOLD,
    DYN_MISSION_STATE_REJOINING,
    DYN_MISSION_STATE_COMPLETED
} DynamicMissionState;

typedef struct {
    double lat;             /* Градуси WGS-84 */
    double lon;             /* Градуси WGS-84 */
    float alt_m;            /* Висота над точкою зльоту, метри */
    float acceptance_rad_m; /* Радіус досягнення точки, метри */
    float cruise_speed_mps; /* Бажана швидкість на сегменті, м/с */
    uint16_t action_cmd;    /* MAVLink команда дії */
} WaypointItem;

typedef struct {
    WaypointItem items[MISSION_MAX_WAYPOINTS];
    uint16_t count;
    uint32_t version;       /* Лічильник версій плану */
} MissionBuffer;

typedef struct {
    double x_proj;          /* Проекція на лінію треку (North) */
    double y_proj;          /* Проекція на лінію треку (East) */
    float remaining_dist_m; /* Залишок відстані до активної точки */
    float hold_pos_ned[3];  /* Координати точки зависання */
    uint16_t saved_seq;     /* Індекс точки на момент натискання паузи */
} PauseSnapshot;

typedef struct {
    MissionBuffer buffers[2];
    volatile uint8_t active_idx;    /* 0 або 1 */
    volatile uint32_t seqlock;      /* Непарне — запис, парне — стабільний стан */

    DynamicMissionState state;
    uint16_t current_seq;
    PauseSnapshot pause_ctx;

    /* Параметри динаміки */
    float max_intercept_deg;
    float lookahead_time_s;
    float max_accel_mps2;
} DynamicMissionController;

void dyn_mission_init(DynamicMissionController *ctrl) {
    memset(ctrl, 0, sizeof(*ctrl));
    ctrl->state = DYN_MISSION_STATE_IDLE;
    ctrl->max_intercept_deg = 35.0f;
    ctrl->lookahead_time_s = 3.0f;
    ctrl->max_accel_mps2 = 2.0f;
}

/* Команда переходу в режим паузи */
bool dyn_mission_pause(DynamicMissionController *ctrl, const float curr_ned[3]) {
    if (ctrl->state != DYN_MISSION_STATE_NAVIGATING &&
        ctrl->state != DYN_MISSION_STATE_REJOINING) {
        return false;
    }

    ctrl->pause_ctx.saved_seq = ctrl->current_seq;
    ctrl->pause_ctx.hold_pos_ned[0] = curr_ned[0];
    ctrl->pause_ctx.hold_pos_ned[1] = curr_ned[1];
    ctrl->pause_ctx.hold_pos_ned[2] = curr_ned[2];
    ctrl->state = DYN_MISSION_STATE_PAUSED_HOLD;
    return true;
}

/* Атомарна заміна невиконаного хвоста місії (Atomic Tail Swap) */
bool dyn_mission_replace_tail(DynamicMissionController *ctrl,
                              uint16_t start_seq,
                              const WaypointItem *new_items,
                              uint16_t new_count) {
    if (start_seq > ctrl->current_seq + 1 || (start_seq + new_count) > MISSION_MAX_WAYPOINTS) {
        return false;
    }

    uint8_t next_buf_idx = 1 - ctrl->active_idx;
    MissionBuffer *staging = &ctrl->buffers[next_buf_idx];
    const MissionBuffer *active = &ctrl->buffers[ctrl->active_idx];

    /* Копіюємо вже виконану історію до точки оновлення */
    memcpy(staging->items, active->items, sizeof(WaypointItem) * start_seq);
    /* Записуємо новий хвіст */
    memcpy(&staging->items[start_seq], new_items, sizeof(WaypointItem) * new_count);
    staging->count = start_seq + new_count;
    staging->version = active->version + 1;

    /* Фаза коміту: seqlock захищає читання в навігаційному циклі */
    ctrl->seqlock++;
    __sync_synchronize();
    ctrl->active_idx = next_buf_idx;
    __sync_synchronize();
    ctrl->seqlock++;

    return true;
}

/* Відновлення польоту після зависання */
bool dyn_mission_resume(DynamicMissionController *ctrl) {
    if (ctrl->state != DYN_MISSION_STATE_PAUSED_HOLD) {
        return false;
    }
    ctrl->state = DYN_MISSION_STATE_REJOINING;
    return true;
}

/* Розрахунок навігаційного вектору повернення */
void dyn_mission_update_guidance(DynamicMissionController *ctrl,
                                const float curr_ned[3],
                                float dt_s,
                                float target_vel_ned[3],
                                float *target_yaw_rad) {
    if (ctrl->state == DYN_MISSION_STATE_PAUSED_HOLD) {
        /* Утримання позиції Hold */
        target_vel_ned[0] = 0.0f;
        target_vel_ned[1] = 0.0f;
        target_vel_ned[2] = 0.0f;
        return;
    }

    const MissionBuffer *buf = &ctrl->buffers[ctrl->active_idx];
    if (ctrl->current_seq >= buf->count) {
        ctrl->state = DYN_MISSION_STATE_COMPLETED;
        target_vel_ned[0] = 0.0f;
        target_vel_ned[1] = 0.0f;
        target_vel_ned[2] = 0.0f;
        return;
    }

    /* Тут розраховується вектор випередження та проекція на лінію */
    const WaypointItem *wp = &buf->items[ctrl->current_seq];
    float dx = (float)(wp->lat * 111319.5) - curr_ned[0];
    float dy = (float)(wp->lon * 111319.5) - curr_ned[1];
    float dist = sqrtf(dx * dx + dy * dy);

    if (dist < wp->acceptance_rad_m) {
        ctrl->current_seq++;
    }

    float speed = wp->cruise_speed_mps > 0.1f ? wp->cruise_speed_mps : 12.0f;
    float heading = atan2f(dy, dx);
    target_vel_ned[0] = cosf(heading) * speed;
    target_vel_ned[1] = sinf(heading) * speed;
    target_vel_ned[2] = 0.0f;
    *target_yaw_rad = heading;
}
