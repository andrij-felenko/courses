#include <stdbool.h>
#include <stdint.h>
#include <math.h>
#include <string.h>

#define ESCAPE_CRUMB_CAPACITY      128
#define ESCAPE_PROGRESS_WINDOW     50
#define ESCAPE_LIDAR_BEAMS         36
#define ESCAPE_VOXEL_HASH_SIZE     64

typedef struct {
    float x;
    float y;
    float z;
} Vec3;

typedef struct {
    float x;
    float y;
} Vec2;

typedef enum {
    ESCAPE_STATE_MONITOR = 0,
    ESCAPE_STATE_EVALUATE_TRAP,
    ESCAPE_STATE_VERTICAL,
    ESCAPE_STATE_BACKTRACK,
    ESCAPE_STATE_WALL_FOLLOW,
    ESCAPE_STATE_REPLAN
} EscapeFsmState;

typedef struct {
    Vec3 buffer[ESCAPE_CRUMB_CAPACITY];
    uint16_t head;
    uint16_t count;
    float min_spacing_sq;
} CrumbRingBuffer;

typedef struct {
    float angle_rad;
    float range_m;
} LidarBeam;

typedef struct {
    int16_t x;
    int16_t y;
    uint16_t visit_count;
} VoxelEntry;

typedef struct {
    /* Налаштування алгоритму */
    float loop_dt;
    float progress_threshold_m;
    float backtrack_target_dist_m;
    float vertical_step_m;
    float wall_distance_target_m;
    float cooldown_duration_s;
    float max_oscillation_ratio;

    /* Внутрішній стан детектора */
    float progress_history[ESCAPE_PROGRESS_WINDOW];
    float speed_history[ESCAPE_PROGRESS_WINDOW];
    Vec3 pos_history[ESCAPE_PROGRESS_WINDOW];
    uint8_t window_idx;
    bool window_filled;

    CrumbRingBuffer crumbs;
    VoxelEntry voxel_table[ESCAPE_VOXEL_HASH_SIZE];
    EscapeFsmState state;
    
    uint16_t backtrack_idx;
    float backtrack_accum_dist;
    float target_altitude_z;
    float cooldown_timer;

    Vec3 trap_entry_pos;
    Vec3 initial_goal_pos;
} LocalMinimaEscapeModule;

static inline float vec3_len_sq(const Vec3* v) {
    return v->x * v->x + v->y * v->y + v->z * v->z;
}

static inline float vec3_len(const Vec3* v) {
    return sqrtf(vec3_len_sq(v));
}

static inline float vec3_dist_sq(const Vec3* a, const Vec3* b) {
    float dx = a->x - b->x;
    float dy = a->y - b->y;
    float dz = a->z - b->z;
    return dx * dx + dy * dy + dz * dz;
}

static inline float vec3_dist(const Vec3* a, const Vec3* b) {
    return sqrtf(vec3_dist_sq(a, b));
}

void local_minima_init(LocalMinimaEscapeModule* mod, float dt) {
    memset(mod, 0, sizeof(LocalMinimaEscapeModule));
    mod->loop_dt = dt;
    mod->progress_threshold_m = 0.30f;       /* Потрібно мінімум 30 см за вікно */
    mod->backtrack_target_dist_m = 4.5f;     /* 4.5 метра відкату */
    mod->vertical_step_m = 3.0f;             /* 3 метри підйому вгору */
    mod->wall_distance_target_m = 1.5f;      /* 1.5 метра від стіни */
    mod->cooldown_duration_s = 5.0f;         /* 5 секунд захисного таймера */
    mod->max_oscillation_ratio = 4.0f;       /* Поріг автоколивань L_path / R_disp */
    mod->crumbs.min_spacing_sq = 0.25f;      /* Запис крихти через кожні 0.5 м */
    mod->state = ESCAPE_STATE_MONITOR;
}

void crumbs_add(CrumbRingBuffer* rb, const Vec3* p) {
    if (rb->count > 0) {
        uint16_t last_idx = (rb->head + ESCAPE_CRUMB_CAPACITY - 1) % ESCAPE_CRUMB_CAPACITY;
        if (vec3_dist_sq(&rb->buffer[last_idx], p) < rb->min_spacing_sq) {
            return;
        }
    }
    rb->buffer[rb->head] = *p;
    rb->head = (rb->head + 1) % ESCAPE_CRUMB_CAPACITY;
    if (rb->count < ESCAPE_CRUMB_CAPACITY) {
        rb->count++;
    }
}

/* Оновлення воксельної сітки відвідування */
static void update_voxel_tracker(LocalMinimaEscapeModule* mod, const Vec3* pos) {
    int16_t vx = (int16_t)floorf(pos->x / 0.5f);
    int16_t vy = (int16_t)floorf(pos->y / 0.5f);
    uint8_t hash = (uint8_t)(((vx * 73856093) ^ (vy * 19349663)) % ESCAPE_VOXEL_HASH_SIZE);

    if (mod->voxel_table[hash].x == vx && mod->voxel_table[hash].y == vy) {
        mod->voxel_table[hash].visit_count++;
    } else {
        mod->voxel_table[hash].x = vx;
        mod->voxel_table[hash].y = vy;
        mod->voxel_table[hash].visit_count = 1;
    }
}

/* Обчислення дотичного вектора руху вздовж стіни за лідаром */
static Vec2 calculate_wall_tangent(const LidarBeam* beams, uint8_t beam_count, float desired_dist) {
    float min_range = 999.0f;
    float closest_angle = 0.0f;

    for (uint8_t i = 0; i < beam_count; ++i) {
        if (beams[i].range_m > 0.1f && beams[i].range_m < min_range) {
            min_range = beams[i].range_m;
            closest_angle = beams[i].angle_rad;
        }
    }

    if (min_range > 10.0f) {
        /* Немає стіни поруч: рух прямо */
        Vec2 fallback = {1.0f, 0.0f};
        return fallback;
    }

    /* Вектор нормалі до стіни (у системі координат апарата) */
    float nx = cosf(closest_angle);
    float ny = sinf(closest_angle);

    /* Лівосторонній дотичний вектор (поворот нормалі на +90 градусів) */
    float tx = -ny;
    float ty = nx;

    /* Корекція дистанції: якщо занадто близько, відштовхуємося від стіни */
    float dist_err = min_range - desired_dist;
    float corr_gain = 0.6f;

    Vec2 cmd;
    cmd.x = tx + (nx * dist_err * corr_gain);
    cmd.y = ty + (ny * dist_err * corr_gain);

    float norm = sqrtf(cmd.x * cmd.x + cmd.y * cmd.y);
    if (norm > 0.001f) {
        cmd.x /= norm;
        cmd.y /= norm;
    }
    return cmd;
}

bool local_minima_step(LocalMinimaEscapeModule* mod,
                       const Vec3* cur_pos,
                       const Vec3* cur_vel,
                       const Vec3* goal_pos,
                       bool thruster_active,
                       float top_clearance_m,
                       const LidarBeam* lidar_beams,
                       uint8_t lidar_beam_count,
                       Vec3* out_setpoint,
                       bool* out_replan_needed) {
    *out_replan_needed = false;

    if (mod->cooldown_timer > 0.0f) {
        mod->cooldown_timer -= mod->loop_dt;
    }

    switch (mod->state) {
    case ESCAPE_STATE_MONITOR: {
        crumbs_add(&mod->crumbs, cur_pos);
        update_voxel_tracker(mod, cur_pos);

        /* 1. Проекція поточної швидкості на промінь до цілі */
        Vec3 to_goal = {
            goal_pos->x - cur_pos->x,
            goal_pos->y - cur_pos->y,
            goal_pos->z - cur_pos->z
        };
        float dist_goal = vec3_len(&to_goal);

        float v_prog = 0.0f;
        if (dist_goal > 0.01f) {
            v_prog = (cur_vel->x * to_goal.x + cur_vel->y * to_goal.y + cur_vel->z * to_goal.z) / dist_goal;
        }

        mod->progress_history[mod->window_idx] = (v_prog > 0.0f) ? (v_prog * mod->loop_dt) : 0.0f;
        mod->speed_history[mod->window_idx] = vec3_len(cur_vel) * mod->loop_dt;
        mod->pos_history[mod->window_idx] = *cur_pos;

        mod->window_idx = (mod->window_idx + 1) % ESCAPE_PROGRESS_WINDOW;
        if (mod->window_idx == 0) {
            mod->window_filled = true;
        }

        if (mod->window_filled && mod->cooldown_timer <= 0.0f && thruster_active) {
            float total_prog = 0.0f;
            float total_path = 0.0f;
            Vec3 pos_mean = {0.0f, 0.0f, 0.0f};

            for (uint8_t i = 0; i < ESCAPE_PROGRESS_WINDOW; ++i) {
                total_prog += mod->progress_history[i];
                total_path += mod->speed_history[i];
                pos_mean.x += mod->pos_history[i].x;
                pos_mean.y += mod->pos_history[i].y;
                pos_mean.z += mod->pos_history[i].z;
            }
            pos_mean.x /= (float)ESCAPE_PROGRESS_WINDOW;
            pos_mean.y /= (float)ESCAPE_PROGRESS_WINDOW;
            pos_mean.z /= (float)ESCAPE_PROGRESS_WINDOW;

            float max_disp = 0.0f;
            for (uint8_t i = 0; i < ESCAPE_PROGRESS_WINDOW; ++i) {
                float d = vec3_dist(&mod->pos_history[i], &pos_mean);
                if (d > max_disp) {
                    max_disp = d;
                }
            }

            /* Перевірка двох критеріїв: брак наближення або автоколивання */
            bool stuck_by_progress = (total_prog < mod->progress_threshold_m);
            bool stuck_by_oscillation = (total_path > 3.0f && (total_path / fmaxf(max_disp, 0.1f)) > mod->max_oscillation_ratio);

            if ((stuck_by_progress || stuck_by_oscillation) && mod->crumbs.count > 4) {
                mod->state = ESCAPE_STATE_EVALUATE_TRAP;
                mod->trap_entry_pos = *cur_pos;
                mod->initial_goal_pos = *goal_pos;
            }
        }
        break;
    }

    case ESCAPE_STATE_EVALUATE_TRAP: {
        /* Перевірка доступності вертикального виходу */
        if (top_clearance_m >= mod->vertical_step_m + 1.0f) {
            mod->state = ESCAPE_STATE_VERTICAL;
            mod->target_altitude_z = cur_pos->z + mod->vertical_step_m;
        } else if (mod->crumbs.count > 2) {
            mod->state = ESCAPE_STATE_BACKTRACK;
            mod->backtrack_accum_dist = 0.0f;
            mod->backtrack_idx = (mod->crumbs.head + ESCAPE_CRUMB_CAPACITY - 1) % ESCAPE_CRUMB_CAPACITY;
        } else {
            mod->state = ESCAPE_STATE_WALL_FOLLOW;
        }
        break;
    }

    case ESCAPE_STATE_VERTICAL: {
        out_setpoint->x = cur_pos->x;
        out_setpoint->y = cur_pos->y;
        out_setpoint->z = mod->target_altitude_z;

        if (fabsf(cur_pos->z - mod->target_altitude_z) < 0.3f) {
            mod->state = ESCAPE_STATE_REPLAN;
        }
        return true;
    }

    case ESCAPE_STATE_BACKTRACK: {
        if (mod->crumbs.count == 0) {
            mod->state = ESCAPE_STATE_REPLAN;
            break;
        }

        Vec3 target_crumb = mod->crumbs.buffer[mod->backtrack_idx];
        *out_setpoint = target_crumb;

        float d_crumb = vec3_dist(cur_pos, &target_crumb);
        if (d_crumb < 0.6f) {
            mod->backtrack_accum_dist += d_crumb;
            if (mod->crumbs.count > 1) {
                mod->backtrack_idx = (mod->backtrack_idx + ESCAPE_CRUMB_CAPACITY - 1) % ESCAPE_CRUMB_CAPACITY;
                mod->crumbs.count--;
            } else {
                mod->crumbs.count = 0;
            }
        }

        if (mod->backtrack_accum_dist >= mod->backtrack_target_dist_m || mod->crumbs.count == 0) {
            mod->state = ESCAPE_STATE_REPLAN;
        }
        return true;
    }

    case ESCAPE_STATE_WALL_FOLLOW: {
        Vec2 tangent = calculate_wall_tangent(lidar_beams, lidar_beam_count, mod->wall_distance_target_m);
        out_setpoint->x = cur_pos->x + tangent.x * 1.5f;
        out_setpoint->y = cur_pos->y + tangent.y * 1.5f;
        out_setpoint->z = cur_pos->z;

        /* Умова виходу за Bug2: перетин лінії m-line ближче до мети */
        float cur_dist_to_goal = vec3_dist(cur_pos, &mod->initial_goal_pos);
        float trap_dist_to_goal = vec3_dist(&mod->trap_entry_pos, &mod->initial_goal_pos);

        if (cur_dist_to_goal < trap_dist_to_goal - 1.0f) {
            mod->state = ESCAPE_STATE_REPLAN;
        }
        return true;
    }

    case ESCAPE_STATE_REPLAN: {
        *out_replan_needed = true;
        mod->cooldown_timer = mod->cooldown_duration_s;
        mod->state = ESCAPE_STATE_MONITOR;
        break;
    }
    }

    return false;
}
