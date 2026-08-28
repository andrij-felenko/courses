#include <stdio.h>
#include <stdbool.h>
#include <stdint.h>
#include <math.h>

#define MAX_TRACKS 8
#define CONFIRMATION_THRESHOLD_M 3
#define HISTORY_WINDOW_N 4
#define MAX_LOST_FRAMES 5

/* Класифікація статусу арбітражу */
typedef enum {
    ARBITRATION_TENTATIVE = 0,
    ARBITRATION_VALIDATING,
    ARBITRATION_CONFIRMED,
    ARBITRATION_COASTING,
    ARBITRATION_REJECTED
} ArbitrationState;

/* Класи об'єктів та їхні фізичні габарити */
typedef enum {
    CLASS_PERSON = 0,
    CLASS_VEHICLE,
    CLASS_OBSTACLE_BOX,
    CLASS_COUNT
} ObjectClass;

typedef struct {
    float h_min; /* мінімальна фізична висота (м) */
    float h_max; /* максимальна фізична висота (м) */
    float v_max; /* максимальна швидкість (м/с) */
    float a_max; /* максимальне прискорення (м/с^2) */
} ClassPhysicsLimits;

static const ClassPhysicsLimits CLASS_LIMITS[CLASS_COUNT] = {
    [CLASS_PERSON]       = { .h_min = 0.6f, .h_max = 2.0f, .v_max = 8.0f,  .a_max = 12.0f },
    [CLASS_VEHICLE]      = { .h_min = 1.2f, .h_max = 3.5f, .v_max = 40.0f, .a_max = 15.0f },
    [CLASS_OBSTACLE_BOX] = { .h_min = 0.2f, .h_max = 2.5f, .v_max = 2.0f,  .a_max = 5.0f  }
};

/* Внутрішні параметри камери (Intrinsics) */
typedef struct {
    float fx;
    float fy;
    float cx;
    float cy;
} CameraIntrinsics;

/* Вихід детектора нейромережі */
typedef struct {
    float u_min;
    float v_min;
    float u_max;
    float v_max;
    float score;
    ObjectClass cls;
} BoundingBoxDetection;

/* Дані активного далекоміра (ToF / Radar) */
typedef struct {
    float distance_m; /* дистанція за променем */
    float offset_x;   /* зсув сенсора від камери X */
    float offset_y;   /* зсув сенсора від камери Y */
    float offset_z;   /* зсув сенсора від камери Z */
    bool valid;       /* прапорець валідності сигналу */
} RangeSensorData;

/* Трек об'єкта */
typedef struct {
    uint32_t track_id;
    ArbitrationState state;
    ObjectClass cls;
    float pos_x;
    float pos_y;
    float pos_z;
    float vel_x;
    float vel_y;
    float vel_z;
    uint8_t hit_history; /* бітова маска останніх N кадрів */
    uint8_t lost_counter;
    bool is_active;
} ObjectTrack;

typedef struct {
    CameraIntrinsics cam;
    ObjectTrack tracks[MAX_TRACKS];
    uint32_t next_track_id;
} ObstacleVerifier;

void verifier_init(ObstacleVerifier* v, float fx, float fy, float cx, float cy) {
    v->cam.fx = fx;
    v->cam.fy = fy;
    v->cam.cx = cx;
    v->cam.cy = cy;
    v->next_track_id = 1;
    for (int i = 0; i < MAX_TRACKS; ++i) {
        v->tracks[i].is_active = false;
        v->tracks[i].state = ARBITRATION_REJECTED;
    }
}

/* 1. Геометрична верифікація масштабу */
bool verify_geometry(const CameraIntrinsics* cam, const BoundingBoxDetection* det, float distance_m) {
    if (distance_m < 0.1f) return false;
    
    float h_measured_px = det->v_max - det->v_min;
    if (h_measured_px <= 1.0f) return false;

    const ClassPhysicsLimits* lim = &CLASS_LIMITS[det->cls];
    float h_expected_min_px = (cam->fy * lim->h_min) / distance_m;
    float h_expected_max_px = (cam->fy * lim->h_max) / distance_m;

    /* Допуск 30% на кути нахилу камери та неточності регресії меж */
    float tol = 0.30f;
    if (h_measured_px < h_expected_min_px * (1.0f - tol)) return false;
    if (h_measured_px > h_expected_max_px * (1.0f + tol)) return false;

    return true;
}

/* 2. Сенсорний крос-чекінг із далекоміром */
bool verify_sensor_cross_check(const CameraIntrinsics* cam, const BoundingBoxDetection* det, const RangeSensorData* rng) {
    if (!rng->valid || rng->distance_m <= 0.05f) return false;

    /* Проєкція точки відбиття далекоміра на матрицю камери */
    float z_cam = rng->distance_m + rng->offset_z;
    if (z_cam <= 0.05f) return false;

    float x_cam = rng->offset_x;
    float y_cam = rng->offset_y;

    float u_proj = cam->cx + cam->fx * (x_cam / z_cam);
    float v_proj = cam->cy + cam->fy * (y_cam / z_cam);

    /* Перевіряємо потрапляння проєкції променя у bounding box */
    if (u_proj >= det->u_min && u_proj <= det->u_max &&
        v_proj >= det->v_min && v_proj <= det->v_max) {
        return true;
    }

    return false;
}

/* 3. Кінематичний строб */
bool verify_kinematics(const ObjectTrack* trk, float meas_x, float meas_y, float meas_z, float dt_sec) {
    if (dt_sec <= 0.0f) return false;

    float pred_x = trk->pos_x + trk->vel_x * dt_sec;
    float pred_y = trk->pos_y + trk->vel_y * dt_sec;
    float pred_z = trk->pos_z + trk->vel_z * dt_sec;

    float dx = meas_x - pred_x;
    float dy = meas_y - pred_y;
    float dz = meas_z - pred_z;
    float dist_sq = dx * dx + dy * dy + dz * dz;

    const ClassPhysicsLimits* lim = &CLASS_LIMITS[trk->cls];
    /* Максимальний радіус стробу: 0.5 * a_max * dt^2 + похибка вимірювання (0.35 м) */
    float r_gate = 0.5f * lim->a_max * dt_sec * dt_sec + 0.35f;
    
    return (dist_sq <= (r_gate * r_gate));
}

/* Оновлення автомата станів арбітражу */
void verifier_update(ObstacleVerifier* v, const BoundingBoxDetection* detections, size_t det_count,
                     const RangeSensorData* range, float dt_sec) {
    /* 1. Позначити всі треки як неоновлені в цьому кадрі */
    bool track_matched[MAX_TRACKS] = { false };

    /* 2. Обробка виявлень */
    for (size_t i = 0; i < det_count; ++i) {
        const BoundingBoxDetection* det = &detections[i];
        if (det->score < 0.40f) continue;

        /* Використовуємо далекомір або проєкційну глибину */
        float est_dist = range->valid ? range->distance_m : 2.5f;

        /* Геометричний фільтр */
        if (!verify_geometry(&v->cam, det, est_dist)) {
            continue; /* Галюцинація розміру відкинута */
        }

        /* Оцінка 3D координат центру об'єкта */
        float u_c = (det->u_min + det->u_max) * 0.5f;
        float v_c = (det->v_min + det->v_max) * 0.5f;
        float pos_z = est_dist;
        float pos_x = (u_c - v->cam.cx) * pos_z / v->cam.fx;
        float pos_y = (v_c - v->cam.cy) * pos_z / v->cam.fy;

        /* Зіставлення з наявними треками */
        int matched_idx = -1;
        float min_dist_sq = 1e9f;

        for (int t = 0; t < MAX_TRACKS; ++t) {
            if (!v->tracks[t].is_active || track_matched[t]) continue;
            if (v->tracks[t].cls != det->cls) continue;

            if (verify_kinematics(&v->tracks[t], pos_x, pos_y, pos_z, dt_sec)) {
                float dx = pos_x - v->tracks[t].pos_x;
                float dy = pos_y - v->tracks[t].pos_y;
                float dz = pos_z - v->tracks[t].pos_z;
                float d_sq = dx * dx + dy * dy + dz * dz;
                if (d_sq < min_dist_sq) {
                    min_dist_sq = d_sq;
                    matched_idx = t;
                }
            }
        }

        if (matched_idx >= 0) {
            /* Оновлення існуючого треку */
            ObjectTrack* trk = &v->tracks[matched_idx];
            track_matched[matched_idx] = true;
            trk->lost_counter = 0;
            trk->hit_history = ((trk->hit_history << 1) | 1) & ((1 << HISTORY_WINDOW_N) - 1);

            /* Оцінка швидкості згладженим фільтром */
            trk->vel_x = 0.7f * trk->vel_x + 0.3f * ((pos_x - trk->pos_x) / dt_sec);
            trk->vel_y = 0.7f * trk->vel_y + 0.3f * ((pos_y - trk->pos_y) / dt_sec);
            trk->vel_z = 0.7f * trk->vel_z + 0.3f * ((pos_z - trk->pos_z) / dt_sec);
            trk->pos_x = pos_x;
            trk->pos_y = pos_y;
            trk->pos_z = pos_z;

            /* Рахуємо кількість попадань у вікні N */
            int hits = 0;
            for (int b = 0; b < HISTORY_WINDOW_N; ++b) {
                if (trk->hit_history & (1 << b)) hits++;
            }

            /* Зміна станів FSM */
            if (trk->state == ARBITRATION_TENTATIVE && hits >= 2) {
                trk->state = ARBITRATION_VALIDATING;
            }
            if (trk->state == ARBITRATION_VALIDATING && hits >= CONFIRMATION_THRESHOLD_M) {
                trk->state = ARBITRATION_CONFIRMED;
            }
            if (trk->state == ARBITRATION_COASTING) {
                trk->state = ARBITRATION_CONFIRMED;
            }
        } else {
            /* Створення нового треку-кандидата у вільному слоті */
            for (int t = 0; t < MAX_TRACKS; ++t) {
                if (!v->tracks[t].is_active) {
                    v->tracks[t].track_id = v->next_track_id++;
                    v->tracks[t].is_active = true;
                    v->tracks[t].state = ARBITRATION_TENTATIVE;
                    v->tracks[t].cls = det->cls;
                    v->tracks[t].pos_x = pos_x;
                    v->tracks[t].pos_y = pos_y;
                    v->tracks[t].pos_z = pos_z;
                    v->tracks[t].vel_x = 0.0f;
                    v->tracks[t].vel_y = 0.0f;
                    v->tracks[t].vel_z = 0.0f;
                    v->tracks[t].hit_history = 1;
                    v->tracks[t].lost_counter = 0;
                    track_matched[t] = true;
                    break;
                }
            }
        }
    }

    /* 3. Оновлення незбіжних треків (Coast / Drop) */
    for (int t = 0; t < MAX_TRACKS; ++t) {
        if (!v->tracks[t].is_active || track_matched[t]) continue;

        ObjectTrack* trk = &v->tracks[t];
        trk->lost_counter++;
        trk->hit_history = (trk->hit_history << 1) & ((1 << HISTORY_WINDOW_N) - 1);

        /* Екстраполяція руху */
        trk->pos_x += trk->vel_x * dt_sec;
        trk->pos_y += trk->vel_y * dt_sec;
        trk->pos_z += trk->vel_z * dt_sec;

        if (trk->state == ARBITRATION_CONFIRMED) {
            trk->state = ARBITRATION_COASTING;
        }

        if (trk->lost_counter >= MAX_LOST_FRAMES || trk->state == ARBITRATION_TENTATIVE) {
            trk->state = ARBITRATION_REJECTED;
            trk->is_active = false;
        }
    }
}
