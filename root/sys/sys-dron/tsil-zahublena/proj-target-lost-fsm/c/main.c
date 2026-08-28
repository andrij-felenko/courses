#include <stdbool.h>
#include <stdint.h>
#include <math.h>

#define REID_EMBEDDING_DIM 128
#define PI_CONST 3.14159265358979323846f

typedef enum {
    TRACKER_STATE_TRACKING = 0,
    TRACKER_STATE_COAST,
    TRACKER_STATE_SEARCH,
    TRACKER_STATE_DISENGAGED
} tracker_state_t;

typedef struct {
    float x;
    float y;
    float z;
} vec3_t;

typedef struct {
    float pan;
    float tilt;
} gimbal_angles_t;

typedef struct {
    vec3_t pos;
    vec3_t vel;
    float cov_pos[3];       /* діагональні елементи коваріації позиції */
    float descriptor[REID_EMBEDDING_DIM];
    bool valid;
} detection_t;

typedef struct {
    float t_coast_limit;    /* секунди */
    float t_search_limit;   /* секунди */
    float spiral_a;         /* початковий радіус спіралі (рад) */
    float spiral_b;         /* крок витка спіралі (рад/рад) */
    float spiral_omega;     /* кутова швидкість обходу (рад/с) */
    float gate_threshold;   /* квадрат відстані Махаланобіса */
    float reid_threshold;   /* мінімальна косинусна схожість */
    float process_noise;    /* приріст дисперсії при екстраполяції */
    float max_gimbal_rate;  /* обмеження кутової швидкості підвісу (рад/с) */
} tracker_config_t;

typedef struct {
    tracker_state_t state;
    vec3_t est_pos;
    vec3_t est_vel;
    float cov_pos[3];
    float ref_descriptor[REID_EMBEDDING_DIM];
    float state_timer;
    float search_theta;
    gimbal_angles_t gimbal_cmd;
    tracker_config_t config;
} target_lost_fsm_t;

/* Обчислення косинусної схожості дескрипторів Re-ID */
static float calc_reid_similarity(const float *a, const float *b, uint16_t dim) {
    float dot = 0.0f;
    float norm_a = 0.0f;
    float norm_b = 0.0f;
    for (uint16_t i = 0; i < dim; ++i) {
        dot += a[i] * b[i];
        norm_a += a[i] * a[i];
        norm_b += b[i] * b[i];
    }
    float denom = sqrtf(norm_a) * sqrtf(norm_b);
    return (denom > 1e-6f) ? (dot / denom) : 0.0f;
}

/* Перевірка просторового стробу Махаланобіса (діагональне наближення) */
static bool check_spatial_gate(const vec3_t *meas, const vec3_t *est, const float cov[3], float thresh) {
    float dx = meas->x - est->x;
    float dy = meas->y - est->y;
    float dz = meas->z - est->z;
    
    float sx = cov[0] > 1e-4f ? cov[0] : 1e-4f;
    float sy = cov[1] > 1e-4f ? cov[1] : 1e-4f;
    float sz = cov[2] > 1e-4f ? cov[2] : 1e-4f;

    float dist_sq = (dx * dx) / sx + (dy * dy) / sy + (dz * dz) / sz;
    return dist_sq <= thresh;
}

/* Ініціалізація автомата */
void target_lost_fsm_init(target_lost_fsm_t *fsm, const tracker_config_t *cfg) {
    fsm->state = TRACKER_STATE_DISENGAGED;
    fsm->est_pos = (vec3_t){0.0f, 0.0f, 0.0f};
    fsm->est_vel = (vec3_t){0.0f, 0.0f, 0.0f};
    fsm->cov_pos[0] = 1.0f;
    fsm->cov_pos[1] = 1.0f;
    fsm->cov_pos[2] = 1.0f;
    fsm->state_timer = 0.0f;
    fsm->search_theta = 0.0f;
    fsm->gimbal_cmd = (gimbal_angles_t){0.0f, 0.0f};
    fsm->config = *cfg;
}

/* Основний такт оновлення FSM */
void target_lost_fsm_update(target_lost_fsm_t *fsm, const detection_t *det, float dt) {
    bool reacquired = false;

    /* Валідація вхідної детекції, якщо вона надійшла */
    if (det != NULL && det->valid) {
        bool in_gate = true;
        bool reid_ok = true;

        if (fsm->state == TRACKER_STATE_COAST || fsm->state == TRACKER_STATE_SEARCH) {
            in_gate = check_spatial_gate(&det->pos, &fsm->est_pos, fsm->cov_pos, fsm->config.gate_threshold);
            float sim = calc_reid_similarity(det->descriptor, fsm->ref_descriptor, REID_EMBEDDING_DIM);
            reid_ok = (sim >= fsm->config.reid_threshold);
        }

        if (in_gate && reid_ok) {
            reacquired = true;
            fsm->est_pos = det->pos;
            fsm->est_vel = det->vel;
            fsm->cov_pos[0] = det->cov_pos[0];
            fsm->cov_pos[1] = det->cov_pos[1];
            fsm->cov_pos[2] = det->cov_pos[2];
            /* Експоненційне оновлення еталонного дескриптора */
            for (uint16_t i = 0; i < REID_EMBEDDING_DIM; ++i) {
                fsm->ref_descriptor[i] = 0.9f * fsm->ref_descriptor[i] + 0.1f * det->descriptor[i];
            }
        }
    }

    /* Логіка станів */
    switch (fsm->state) {
    case TRACKER_STATE_TRACKING:
        if (reacquired) {
            fsm->state_timer = 0.0f;
        } else {
            fsm->state = TRACKER_STATE_COAST;
            fsm->state_timer = 0.0f;
        }
        break;

    case TRACKER_STATE_COAST:
        if (reacquired) {
            fsm->state = TRACKER_STATE_TRACKING;
            fsm->state_timer = 0.0f;
        } else {
            fsm->state_timer += dt;
            /* Кінематична екстраполяція положення цілі */
            fsm->est_pos.x += fsm->est_vel.x * dt;
            fsm->est_pos.y += fsm->est_vel.y * dt;
            fsm->est_pos.z += fsm->est_vel.z * dt;

            /* Зростання невизначеності коваріації */
            fsm->cov_pos[0] += fsm->config.process_noise * dt;
            fsm->cov_pos[1] += fsm->config.process_noise * dt;
            fsm->cov_pos[2] += fsm->config.process_noise * dt;

            if (fsm->state_timer >= fsm->config.t_coast_limit) {
                fsm->state = TRACKER_STATE_SEARCH;
                fsm->state_timer = 0.0f;
                fsm->search_theta = 0.0f;
            }
        }
        break;

    case TRACKER_STATE_SEARCH:
        if (reacquired) {
            fsm->state = TRACKER_STATE_TRACKING;
            fsm->state_timer = 0.0f;
        } else {
            fsm->state_timer += dt;
            /* Генерація траєкторії Архімедової спіралі для підвісу */
            fsm->search_theta += fsm->config.spiral_omega * dt;
            float r = fsm->config.spiral_a + fsm->config.spiral_b * fsm->search_theta;
            fsm->gimbal_cmd.pan = r * cosf(fsm->search_theta);
            fsm->gimbal_cmd.tilt = r * sinf(fsm->search_theta);

            /* Продовження повільного дрейфу екстраполяції */
            fsm->est_pos.x += fsm->est_vel.x * dt * 0.5f;
            fsm->est_pos.y += fsm->est_vel.y * dt * 0.5f;
            fsm->cov_pos[0] += fsm->config.process_noise * dt * 2.0f;
            fsm->cov_pos[1] += fsm->config.process_noise * dt * 2.0f;

            if (fsm->state_timer >= fsm->config.t_search_limit) {
                fsm->state = TRACKER_STATE_DISENGAGED;
                fsm->state_timer = 0.0f;
            }
        }
        break;

    case TRACKER_STATE_DISENGAGED:
        if (reacquired) {
            fsm->state = TRACKER_STATE_TRACKING;
            fsm->state_timer = 0.0f;
        }
        break;
    }
}
