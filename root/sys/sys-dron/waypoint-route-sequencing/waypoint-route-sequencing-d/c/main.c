#include <stdio.h>
#include <stdbool.h>
#include <stdint.h>
#include <math.h>

#define M_PI_F 3.14159265358979323846f
#define DEG_TO_RAD_F (M_PI_F / 180.0f)
#define RAD_TO_DEG_F (180.0f / M_PI_F)
#define CONSTANTS_RADIUS_OF_EARTH 6371000.0f

typedef enum {
    YAW_MODE_ALONG_TRACK = 0,
    YAW_MODE_FIXED       = 1,
    YAW_MODE_ROI         = 2
} yaw_mode_t;

typedef enum {
    SEQ_STATE_IDLE         = 0,
    SEQ_STATE_NAVIGATING   = 1,
    SEQ_STATE_LOITER_HOLD  = 2,
    SEQ_STATE_EXEC_ACTION  = 3,
    SEQ_STATE_ADVANCE_WP   = 4,
    SEQ_STATE_MISSION_DONE = 5
} seq_state_t;

typedef struct {
    double lat;          // Градуси WGS-84
    double lon;          // Градуси WGS-84
    float alt;           // Метри (відносна висота)
    float v_cruise;      // м/с
    float r_acc;         // Радіус кулі досягнення (м)
    float t_hold;        // Час затримки в точці (с)
    float yaw_param;     // Цільовий кут рискання (рад)
    yaw_mode_t yaw_mode; // Режим узгодження курсу
    uint16_t action_id;  // Ідентифікатор команди (наприклад 100 = фотознімок)
    bool fly_through;    // true = плавний обліт, false = зупинка
} waypoint_t;

typedef struct {
    float x; // North (м)
    float y; // East (м)
    float z; // Down (м)
} vec3_t;

typedef struct {
    vec3_t pos;          // Поточна позиція в NED
    vec3_t vel;          // Поточна швидкість в NED
    float yaw;           // Поточний кут рискання (рад)
} vehicle_state_t;

typedef struct {
    vec3_t pos_target;   // Цільова позиція (м)
    vec3_t vel_target;   // Бажаний вектор швидкості (м/с)
    float yaw_target;    // Бажаний кут рискання (рад)
    bool trigger_action; // Сигнал виконання дії
} nav_setpoint_t;

typedef struct {
    const waypoint_t *waypoints;
    size_t count;
    size_t current_index;
    size_t prev_index;

    double home_lat;
    double home_lon;
    float home_alt;

    seq_state_t state;
    float hold_timer;
    vec3_t roi_pos;
    bool roi_active;

    vec3_t curr_wp_ned;
    vec3_t prev_wp_ned;
    vec3_t segment_unit_in;
} mission_sequencer_t;

static float wrap_pi(float angle) {
    while (angle > M_PI_F)  angle -= 2.0f * M_PI_F;
    while (angle < -M_PI_F) angle += 2.0f * M_PI_F;
    return angle;
}

static vec3_t geo_to_ned(double lat, double lon, float alt,
                         double home_lat, double home_lon, float home_alt) {
    double d_lat = (lat - home_lat) * DEG_TO_RAD_F;
    double d_lon = (lon - home_lon) * DEG_TO_RAD_F;
    double lat_rad = home_lat * DEG_TO_RAD_F;

    vec3_t ned;
    ned.x = (float)(d_lat * CONSTANTS_RADIUS_OF_EARTH);
    ned.y = (float)(d_lon * CONSTANTS_RADIUS_OF_EARTH * cos(lat_rad));
    ned.z = -(alt - home_alt);
    return ned;
}

static float vec3_dist_2d(vec3_t a, vec3_t b) {
    float dx = a.x - b.x;
    float dy = a.y - b.y;
    return sqrtf(dx * dx + dy * dy);
}

static float vec3_dot(vec3_t a, vec3_t b) {
    return a.x * b.x + a.y * b.y + a.z * b.z;
}

void sequencer_init(mission_sequencer_t *seq, const waypoint_t *wps, size_t count,
                    double home_lat, double home_lon, float home_alt) {
    seq->waypoints = wps;
    seq->count = count;
    seq->current_index = 0;
    seq->prev_index = 0;
    seq->home_lat = home_lat;
    seq->home_lon = home_lon;
    seq->home_alt = home_alt;
    seq->state = (count > 0) ? SEQ_STATE_NAVIGATING : SEQ_STATE_IDLE;
    seq->hold_timer = 0.0f;
    seq->roi_active = false;

    if (count > 0) {
        seq->prev_wp_ned = geo_to_ned(home_lat, home_lon, home_alt, home_lat, home_lon, home_alt);
        seq->curr_wp_ned = geo_to_ned(wps[0].lat, wps[0].lon, wps[0].alt, home_lat, home_lon, home_alt);
        
        vec3_t seg_in = {
            seq->curr_wp_ned.x - seq->prev_wp_ned.x,
            seq->curr_wp_ned.y - seq->prev_wp_ned.y,
            seq->curr_wp_ned.z - seq->prev_wp_ned.z
        };
        float len = sqrtf(vec3_dot(seg_in, seg_in));
        if (len > 0.001f) {
            seq->segment_unit_in.x = seg_in.x / len;
            seq->segment_unit_in.y = seg_in.y / len;
            seq->segment_unit_in.z = seg_in.z / len;
        } else {
            seq->segment_unit_in = (vec3_t){1.0f, 0.0f, 0.0f};
        }
    }
}

void sequencer_set_roi(mission_sequencer_t *seq, double lat, double lon, float alt) {
    seq->roi_pos = geo_to_ned(lat, lon, alt, seq->home_lat, seq->home_lon, seq->home_alt);
    seq->roi_active = true;
}

void sequencer_clear_roi(mission_sequencer_t *seq) {
    seq->roi_active = false;
}

static bool check_waypoint_reached(const mission_sequencer_t *seq, const vehicle_state_t *veh, const waypoint_t *wp) {
    float dist_xy = vec3_dist_2d(veh->pos, seq->curr_wp_ned);
    float dist_z = fabsf(veh->pos.z - seq->curr_wp_ned.z);

    // 1. Умова входу в кулю досягнення
    if (dist_xy <= wp->r_acc && dist_z <= (wp->r_acc * 1.5f)) {
        return true;
    }

    // 2. Умова перетину нормальної площини прольоту (Passing Plane)
    vec3_t d_target = {
        veh->pos.x - seq->curr_wp_ned.x,
        veh->pos.y - seq->curr_wp_ned.y,
        veh->pos.z - seq->curr_wp_ned.z
    };
    float s_pass = vec3_dot(d_target, seq->segment_unit_in);

    // Дозволяємо перетин площини, якщо бічне зміщення не перевищує 3-кратний радіус кулі
    if (s_pass >= 0.0f && dist_xy <= (wp->r_acc * 3.0f)) {
        return true;
    }

    return false;
}

nav_setpoint_t sequencer_tick(mission_sequencer_t *seq, const vehicle_state_t *veh, float dt) {
    nav_setpoint_t sp = {0};
    sp.pos_target = seq->curr_wp_ned;
    sp.trigger_action = false;

    if (seq->state == SEQ_STATE_IDLE || seq->state == SEQ_STATE_MISSION_DONE) {
        sp.vel_target = (vec3_t){0.0f, 0.0f, 0.0f};
        sp.yaw_target = veh->yaw;
        return sp;
    }

    const waypoint_t *curr_wp = &seq->waypoints[seq->current_index];

    switch (seq->state) {
    case SEQ_STATE_NAVIGATING: {
        bool reached = check_waypoint_reached(seq, veh, curr_wp);

        if (reached) {
            if (curr_wp->fly_through && curr_wp->t_hold <= 0.001f) {
                // Плавний обліт без зупинки: одразу перемикаємо на наступну точку
                seq->state = SEQ_STATE_ADVANCE_WP;
            } else {
                // Зупинка в точці: скидаємо швидкість і запускаємо таймер
                seq->state = SEQ_STATE_LOITER_HOLD;
                seq->hold_timer = curr_wp->t_hold;
            }
        } else {
            // Напрям швидкості вздовж лінії до цілі
            vec3_t dir = {
                seq->curr_wp_ned.x - veh->pos.x,
                seq->curr_wp_ned.y - veh->pos.y,
                seq->curr_wp_ned.z - veh->pos.z
            };
            float dist = sqrtf(vec3_dot(dir, dir));
            if (dist > 0.001f) {
                sp.vel_target.x = (dir.x / dist) * curr_wp->v_cruise;
                sp.vel_target.y = (dir.y / dist) * curr_wp->v_cruise;
                sp.vel_target.z = (dir.z / dist) * curr_wp->v_cruise;
            }
        }
        break;
    }

    case SEQ_STATE_LOITER_HOLD: {
        sp.vel_target = (vec3_t){0.0f, 0.0f, 0.0f};
        seq->hold_timer -= dt;
        if (seq->hold_timer <= 0.0f) {
            seq->state = (curr_wp->action_id != 0) ? SEQ_STATE_EXEC_ACTION : SEQ_STATE_ADVANCE_WP;
        }
        break;
    }

    case SEQ_STATE_EXEC_ACTION: {
        sp.vel_target = (vec3_t){0.0f, 0.0f, 0.0f};
        sp.trigger_action = true;
        // Після генерації імпульсу дії переходимо до наступної точки
        seq->state = SEQ_STATE_ADVANCE_WP;
        break;
    }

    case SEQ_STATE_ADVANCE_WP: {
        seq->prev_index = seq->current_index;
        seq->current_index++;

        if (seq->current_index >= seq->count) {
            seq->state = SEQ_STATE_MISSION_DONE;
            sp.vel_target = (vec3_t){0.0f, 0.0f, 0.0f};
        } else {
            seq->prev_wp_ned = seq->curr_wp_ned;
            const waypoint_t *next_wp = &seq->waypoints[seq->current_index];
            seq->curr_wp_ned = geo_to_ned(next_wp->lat, next_wp->lon, next_wp->alt,
                                          seq->home_lat, seq->home_lon, seq->home_alt);

            vec3_t seg = {
                seq->curr_wp_ned.x - seq->prev_wp_ned.x,
                seq->curr_wp_ned.y - seq->prev_wp_ned.y,
                seq->curr_wp_ned.z - seq->prev_wp_ned.z
            };
            float len = sqrtf(vec3_dot(seg, seg));
            if (len > 0.001f) {
                seq->segment_unit_in.x = seg.x / len;
                seq->segment_unit_in.y = seg.y / len;
                seq->segment_unit_in.z = seg.z / len;
            }
            seq->state = SEQ_STATE_NAVIGATING;
        }
        break;
    }

    default:
        break;
    }

    // Розрахунок цільового кута рискання (Yaw Coordination)
    if (seq->roi_active) {
        float dx = seq->roi_pos.x - veh->pos.x;
        float dy = seq->roi_pos.y - veh->pos.y;
        sp.yaw_target = atan2f(dy, dx);
    } else {
        switch (curr_wp->yaw_mode) {
        case YAW_MODE_FIXED:
            sp.yaw_target = curr_wp->yaw_param;
            break;
        case YAW_MODE_ROI:
            sp.yaw_target = atan2f(seq->roi_pos.y - veh->pos.y, seq->roi_pos.x - veh->pos.x);
            break;
        case YAW_MODE_ALONG_TRACK:
        default: {
            float dx = seq->curr_wp_ned.x - veh->pos.x;
            float dy = seq->curr_wp_ned.y - veh->pos.y;
            if (sqrtf(dx * dx + dy * dy) > 0.5f) {
                sp.yaw_target = atan2f(dy, dx);
            } else {
                sp.yaw_target = veh->yaw;
            }
            break;
        }
        }
    }

    return sp;
}
