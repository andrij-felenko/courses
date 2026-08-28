#include <stdbool.h>
#include <stdint.h>
#include <math.h>
#include <string.h>

#define BREADCRUMB_CAPACITY 128
#define PROGRESS_WINDOW_SIZE 50

typedef struct {
    float x;
    float y;
    float z;
} Vector3f;

typedef enum {
    NAV_STATE_NORMAL = 0,
    NAV_STATE_STUCK_DETECTED,
    NAV_STATE_BACKTRACKING,
    NAV_STATE_REPLAN_TRIGGERED
} NavEscapeState;

typedef struct {
    Vector3f buffer[BREADCRUMB_CAPACITY];
    uint16_t head;
    uint16_t count;
    float min_dist_sq;
} BreadcrumbTracker;

typedef struct {
    float progress_history[PROGRESS_WINDOW_SIZE];
    uint8_t window_idx;
    uint8_t window_filled;
    float window_dt;
    float progress_threshold;
    float max_dispersion_ratio;
    
    BreadcrumbTracker crumbs;
    NavEscapeState state;
    uint16_t backtrack_target_idx;
    float backtrack_dist_accum;
    float backtrack_required_dist;
    float cooldown_timer;
} LocalMinimaEscapeDetector;

static inline float vec3_dist_sq(const Vector3f* a, const Vector3f* b) {
    float dx = a->x - b->x;
    float dy = a->y - b->y;
    float dz = a->z - b->z;
    return dx * dx + dy * dy + dz * dz;
}

static inline float vec3_dist(const Vector3f* a, const Vector3f* b) {
    return sqrtf(vec3_dist_sq(a, b));
}

void escape_detector_init(LocalMinimaEscapeDetector* det, float dt) {
    memset(det, 0, sizeof(LocalMinimaEscapeDetector));
    det->window_dt = dt;
    det->progress_threshold = 0.25f;       /* мінімум 25 см прогресу за вікно */
    det->max_dispersion_ratio = 4.0f;       /* поріг детекції коливань */
    det->crumbs.min_dist_sq = 0.25f;       /* запис крихти кожні 0.5 м */
    det->backtrack_required_dist = 4.0f;    /* відкат на 4 метри назад */
    det->state = NAV_STATE_NORMAL;
}

void breadcrumb_push(BreadcrumbTracker* bt, const Vector3f* pos) {
    if (bt->count > 0) {
        uint16_t last_idx = (bt->head + BREADCRUMB_CAPACITY - 1) % BREADCRUMB_CAPACITY;
        if (vec3_dist_sq(&bt->buffer[last_idx], pos) < bt->min_dist_sq) {
            return;
        }
    }
    bt->buffer[bt->head] = *pos;
    bt->head = (bt->head + 1) % BREADCRUMB_CAPACITY;
    if (bt->count < BREADCRUMB_CAPACITY) {
        bt->count++;
    }
}

bool escape_detector_update(LocalMinimaEscapeDetector* det,
                            const Vector3f* cur_pos,
                            const Vector3f* cur_vel,
                            const Vector3f* goal_pos,
                            bool active_thrust,
                            Vector3f* out_setpoint) {
    if (det->cooldown_timer > 0.0f) {
        det->cooldown_timer -= det->window_dt;
    }

    if (det->state == NAV_STATE_NORMAL) {
        breadcrumb_push(&det->crumbs, cur_pos);

        /* 1. Розрахунок проекції швидкості на промінь до цілі */
        float to_goal_x = goal_pos->x - cur_pos->x;
        float to_goal_y = goal_pos->y - cur_pos->y;
        float to_goal_z = goal_pos->z - cur_pos->z;
        float dist_goal = sqrtf(to_goal_x * to_goal_x + to_goal_y * to_goal_y + to_goal_z * to_goal_z);

        float v_prog = 0.0f;
        if (dist_goal > 0.001f) {
            v_prog = (cur_vel->x * to_goal_x + cur_vel->y * to_goal_y + cur_vel->z * to_goal_z) / dist_goal;
        }

        det->progress_history[det->window_idx] = (v_prog > 0.0f) ? (v_prog * det->window_dt) : 0.0f;
        det->window_idx = (det->window_idx + 1) % PROGRESS_WINDOW_SIZE;
        if (det->window_idx == 0) {
            det->window_filled = 1;
        }

        /* 2. Аналіз накопиченого корисного прогресу */
        if (det->window_filled && det->cooldown_timer <= 0.0f && active_thrust) {
            float total_prog = 0.0f;
            for (int i = 0; i < PROGRESS_WINDOW_SIZE; ++i) {
                total_prog += det->progress_history[i];
            }

            if (total_prog < det->progress_threshold && det->crumbs.count > 4) {
                det->state = NAV_STATE_STUCK_DETECTED;
                det->backtrack_dist_accum = 0.0f;
                det->backtrack_target_idx = (det->crumbs.head + BREADCRUMB_CAPACITY - 1) % BREADCRUMB_CAPACITY;
            }
        }
        return false;
    }

    if (det->state == NAV_STATE_STUCK_DETECTED || det->state == NAV_STATE_BACKTRACKING) {
        det->state = NAV_STATE_BACKTRACKING;

        if (det->crumbs.count == 0) {
            det->state = NAV_STATE_REPLAN_TRIGGERED;
            return true;
        }

        Vector3f target_wp = det->crumbs.buffer[det->backtrack_target_idx];
        *out_setpoint = target_wp;

        float dist_to_wp = vec3_dist(cur_pos, &target_wp);
        if (dist_to_wp < 0.6f) {
            det->backtrack_dist_accum += dist_to_wp;
            if (det->crumbs.count > 1) {
                det->backtrack_target_idx = (det->backtrack_target_idx + BREADCRUMB_CAPACITY - 1) % BREADCRUMB_CAPACITY;
                det->crumbs.count--;
            } else {
                det->crumbs.count = 0;
            }
        }

        if (det->backtrack_dist_accum >= det->backtrack_required_dist || det->crumbs.count == 0) {
            det->state = NAV_STATE_REPLAN_TRIGGERED;
            det->cooldown_timer = 5.0f;
            return true;
        }
    }

    return false;
}
