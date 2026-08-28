#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <math.h>
#include <string.h>
#include <stdint.h>

#define MAX_RAW_POINTS      8192
#define MAX_FILTERED_POINTS 4096
#define HASH_TABLE_SIZE     4099    /* Просте число для хешування */
#define MAX_VOXEL_CELLS     16384
#define VOXEL_SIZE          0.20f   /* 20 см ребро вокселя */
#define CELL_NEIGHBORS_MAX  64

/* Структура просторової точки */
typedef struct {
    float x;
    float y;
    float z;
    float intensity;
} Point3D;

/* Кватерніон орієнтації [w, x, y, z] */
typedef struct {
    float w, x, y, z;
} Quaternion;

/* Стан навігації та кінематики апарата */
typedef struct {
    float x, y, z;          /* Позиція в ENU (м) */
    float vx, vy, vz;       /* Лінійна швидкість (м/с) */
    Quaternion q;           /* Орієнтація у просторі */
    float roll, pitch, yaw; /* Кути Ейлера (рад) */
} VehicleState;

/* Елемент просторової хеш-таблиці для швидкого SOR */
typedef struct {
    int32_t point_indices[CELL_NEIGHBORS_MAX];
    uint16_t count;
    int32_t key_x, key_y, key_z;
    bool active;
} HashCell;

/* Осередок сітки часової персистентності */
typedef struct {
    int32_t vx, vy, vz;
    float weight;
    float last_time_sec;
    bool occupied;
} VoxelEntry;

/* Повний конвеєр фільтрації */
typedef struct {
    HashCell hash_table[HASH_TABLE_SIZE];
    VoxelEntry voxel_grid[MAX_VOXEL_CELLS];
    size_t voxel_count;

    /* Параметри SOR */
    int k_neighbors;
    float alpha_factor;
    float hash_cell_size;

    /* Параметри персистентності */
    float decay_rate;
    float max_weight;
    float occ_threshold;

    /* Параметри безпеки */
    float max_brake_accel;
    float sensor_vfov_rad;
    float safe_margin_m;
} ObstacleFilterPipeline;

/* Ініціалізація структури конвеєра */
void filter_init(ObstacleFilterPipeline* pipe) {
    memset(pipe, 0, sizeof(ObstacleFilterPipeline));
    pipe->k_neighbors = 8;
    pipe->alpha_factor = 1.5f;
    pipe->hash_cell_size = 0.40f;

    pipe->decay_rate = 2.5f;        /* Ваги на секунду */
    pipe->max_weight = 10.0f;
    pipe->occ_threshold = 3.0f;

    pipe->max_brake_accel = 4.0f;   /* м/с^2 */
    pipe->sensor_vfov_rad = 58.0f * (float)M_PI / 180.0f;
    pipe->safe_margin_m = 1.2f;
}

/* Обчислення хеш-ключа */
static inline uint32_t compute_hash(int32_t ix, int32_t iy, int32_t iz) {
    uint32_t h = (uint32_t)(ix * 73856093 ^ iy * 19349663 ^ iz * 83492791);
    return h % HASH_TABLE_SIZE;
}

/* Обертання вектора кватерніоном */
static inline Point3D rotate_vector_by_quat(Point3D v, Quaternion q) {
    float tx = 2.0f * (q.y * v.z - q.z * v.y);
    float ty = 2.0f * (q.z * v.x - q.x * v.z);
    float tz = 2.0f * (q.x * v.y - q.y * v.x);

    Point3D out;
    out.x = v.x + q.w * tx + (q.y * tz - q.z * ty);
    out.y = v.y + q.w * ty + (q.z * tx - q.x * tz);
    out.z = v.z + q.w * tz + (q.x * ty - q.y * tx);
    out.intensity = v.intensity;
    return out;
}

/* 1. Трансформація хмари точок у світову систему координат */
size_t filter_transform_to_world(const Point3D* in_pts, size_t n_pts, 
                                 const VehicleState* state, 
                                 Point3D* out_pts) {
    size_t valid = 0;
    for (size_t i = 0; i < n_pts && valid < MAX_RAW_POINTS; ++i) {
        float r_sq = in_pts[i].x * in_pts[i].x + in_pts[i].y * in_pts[i].y + in_pts[i].z * in_pts[i].z;
        if (r_sq < 0.09f || r_sq > 400.0f) continue; /* Відкидаємо пропелери та нескінченність */

        Point3D rotated = rotate_vector_by_quat(in_pts[i], state->q);
        out_pts[valid].x = rotated.x + state->x;
        out_pts[valid].y = rotated.y + state->y;
        out_pts[valid].z = rotated.z + state->z;
        out_pts[valid].intensity = in_pts[i].intensity;
        valid++;
    }
    return valid;
}

/* 2. Статистичний фільтр викидів (Spatial Hash SOR) */
size_t filter_statistical_outliers(ObstacleFilterPipeline* pipe, 
                                   const Point3D* in_pts, size_t n_pts, 
                                   Point3D* out_pts) {
    if (n_pts < (size_t)pipe->k_neighbors || n_pts == 0) return 0;

    memset(pipe->hash_table, 0, sizeof(pipe->hash_table));
    float inv_cell = 1.0f / pipe->hash_cell_size;

    /* Заповнення просторового хешу */
    for (size_t i = 0; i < n_pts; ++i) {
        int32_t ix = (int32_t)floorf(in_pts[i].x * inv_cell);
        int32_t iy = (int32_t)floorf(in_pts[i].y * inv_cell);
        int32_t iz = (int32_t)floorf(in_pts[i].z * inv_cell);

        uint32_t slot = compute_hash(ix, iy, iz);
        for (size_t probe = 0; probe < 8; ++probe) {
            uint32_t s = (slot + probe) % HASH_TABLE_SIZE;
            if (!pipe->hash_table[s].active) {
                pipe->hash_table[s].active = true;
                pipe->hash_table[s].key_x = ix;
                pipe->hash_table[s].key_y = iy;
                pipe->hash_table[s].key_z = iz;
                pipe->hash_table[s].count = 0;
            }
            if (pipe->hash_table[s].key_x == ix && 
                pipe->hash_table[s].key_y == iy && 
                pipe->hash_table[s].key_z == iz) {
                if (pipe->hash_table[s].count < CELL_NEIGHBORS_MAX) {
                    pipe->hash_table[s].point_indices[pipe->hash_table[s].count++] = (int32_t)i;
                }
                break;
            }
        }
    }

    /* Пошук k найближчих сусідів та розрахунок середніх відстаней */
    float mean_distances[MAX_RAW_POINTS];
    double sum_mean = 0.0;

    for (size_t i = 0; i < n_pts; ++i) {
        int32_t ix = (int32_t)floorf(in_pts[i].x * inv_cell);
        int32_t iy = (int32_t)floorf(in_pts[i].y * inv_cell);
        int32_t iz = (int32_t)floorf(in_pts[i].z * inv_cell);

        float dists[CELL_NEIGHBORS_MAX * 4];
        size_t n_found = 0;

        for (int32_t dx = -1; dx <= 1; ++dx) {
            for (int32_t dy = -1; dy <= 1; ++dy) {
                for (int32_t dz = -1; dz <= 1; ++dz) {
                    uint32_t slot = compute_hash(ix + dx, iy + dy, iz + dz);
                    for (size_t probe = 0; probe < 8; ++probe) {
                        uint32_t s = (slot + probe) % HASH_TABLE_SIZE;
                        if (!pipe->hash_table[s].active) break;
                        if (pipe->hash_table[s].key_x == (ix + dx) && 
                            pipe->hash_table[s].key_y == (iy + dy) && 
                            pipe->hash_table[s].key_z == (iz + dz)) {
                            for (uint16_t c = 0; c < pipe->hash_table[s].count; ++c) {
                                int32_t idx = pipe->hash_table[s].point_indices[c];
                                if ((size_t)idx == i) continue;
                                float ddx = in_pts[i].x - in_pts[idx].x;
                                float ddy = in_pts[i].y - in_pts[idx].y;
                                float ddz = in_pts[i].z - in_pts[idx].z;
                                dists[n_found++] = sqrtf(ddx * ddx + ddy * ddy + ddz * ddz);
                                if (n_found >= (CELL_NEIGHBORS_MAX * 4 - 1)) goto sort_k;
                            }
                            break;
                        }
                    }
                }
            }
        }

    sort_k:
        if (n_found < (size_t)pipe->k_neighbors) {
            mean_distances[i] = 999.0f;
            continue;
        }

        /* Знаходження k найменших відстаней */
        float sum_k = 0.0f;
        for (int k = 0; k < pipe->k_neighbors; ++k) {
            size_t min_idx = (size_t)k;
            for (size_t m = (size_t)k + 1; m < n_found; ++m) {
                if (dists[m] < dists[min_idx]) min_idx = m;
            }
            float tmp = dists[k];
            dists[k] = dists[min_idx];
            dists[min_idx] = tmp;
            sum_k += dists[k];
        }
        mean_distances[i] = sum_k / (float)pipe->k_neighbors;
        sum_mean += mean_distances[i];
    }

    double global_mu = sum_mean / (double)n_pts;
    double sum_sq_diff = 0.0;
    for (size_t i = 0; i < n_pts; ++i) {
        if (mean_distances[i] < 900.0f) {
            double diff = mean_distances[i] - global_mu;
            sum_sq_diff += diff * diff;
        }
    }
    double global_sigma = sqrt(sum_sq_diff / (double)n_pts);
    float threshold = (float)(global_mu + (double)pipe->alpha_factor * global_sigma);

    /* Фільтрація точок за порогом */
    size_t out_count = 0;
    for (size_t i = 0; i < n_pts; ++i) {
        if (mean_distances[i] <= threshold && out_count < MAX_FILTERED_POINTS) {
            out_pts[out_count++] = in_pts[i];
        }
    }
    return out_count;
}

/* 3. Просторово-часова персистентність */
void filter_update_persistence(ObstacleFilterPipeline* pipe, 
                               const Point3D* pts, size_t n_pts, 
                               float time_sec) {
    for (size_t i = 0; i < pipe->voxel_count; ++i) {
        float dt = time_sec - pipe->voxel_grid[i].last_time_sec;
        if (dt > 0.02f) {
            pipe->voxel_grid[i].weight -= pipe->decay_rate * dt;
            pipe->voxel_grid[i].last_time_sec = time_sec;
            if (pipe->voxel_grid[i].weight <= 0.0f) {
                pipe->voxel_grid[i] = pipe->voxel_grid[pipe->voxel_count - 1];
                pipe->voxel_count--;
                i--;
                continue;
            }
        }
        pipe->voxel_grid[i].occupied = (pipe->voxel_grid[i].weight >= pipe->occ_threshold);
    }

    float inv_vox = 1.0f / VOXEL_SIZE;
    for (size_t i = 0; i < n_pts; ++i) {
        int32_t ivx = (int32_t)floorf(pts[i].x * inv_vox);
        int32_t ivy = (int32_t)floorf(pts[i].y * inv_vox);
        int32_t ivz = (int32_t)floorf(pts[i].z * inv_vox);

        bool found = false;
        for (size_t j = 0; j < pipe->voxel_count; ++j) {
            if (pipe->voxel_grid[j].vx == ivx && 
                pipe->voxel_grid[j].vy == ivy && 
                pipe->voxel_grid[j].vz == ivz) {
                pipe->voxel_grid[j].weight += 1.0f;
                if (pipe->voxel_grid[j].weight > pipe->max_weight) {
                    pipe->voxel_grid[j].weight = pipe->max_weight;
                }
                pipe->voxel_grid[j].last_time_sec = time_sec;
                pipe->voxel_grid[j].occupied = (pipe->voxel_grid[j].weight >= pipe->occ_threshold);
                found = true;
                break;
            }
        }

        if (!found && pipe->voxel_count < MAX_VOXEL_CELLS) {
            VoxelEntry* v = &pipe->voxel_grid[pipe->voxel_count++];
            v->vx = ivx;
            v->vy = ivy;
            v->vz = ivz;
            v->weight = 1.0f;
            v->last_time_sec = time_sec;
            v->occupied = false;
        }
    }
}

/* 4. Компенсація сліпих зон та перевірка коридору безпеки */
bool filter_evaluate_safety(const ObstacleFilterPipeline* pipe, 
                            const VehicleState* state, 
                            float* out_max_safe_speed) {
    float speed = sqrtf(state->vx * state->vx + state->vy * state->vy + state->vz * state->vz);
    
    /* Оцінка кута нахилу та обмеження швидкості */
    float pitch_angle = state->pitch;
    float half_vfov = pipe->sensor_vfov_rad * 0.5f;
    float upper_clearance = half_vfov + pitch_angle;

    float max_speed_fov = 15.0f;
    if (upper_clearance < 0.05f) {
        max_speed_fov = 3.0f;
    } else if (upper_clearance < 0.20f) {
        max_speed_fov = 3.0f + (upper_clearance / 0.20f) * 7.0f;
    }
    *out_max_safe_speed = max_speed_fov;

    if (speed < 0.15f) return false;

    /* Розрахунок коридору гальмування */
    float stop_dist = (speed * speed) / (2.0f * pipe->max_brake_accel) + speed * 0.15f + pipe->safe_margin_m;
    float dir_x = state->vx / speed;
    float dir_y = state->vy / speed;
    float dir_z = state->vz / speed;

    for (size_t i = 0; i < pipe->voxel_count; ++i) {
        if (!pipe->voxel_grid[i].occupied) continue;

        float wx = ((float)pipe->voxel_grid[i].vx + 0.5f) * VOXEL_SIZE;
        float wy = ((float)pipe->voxel_grid[i].vy + 0.5f) * VOXEL_SIZE;
        float wz = ((float)pipe->voxel_grid[i].vz + 0.5f) * VOXEL_SIZE;

        float rx = wx - state->x;
        float ry = wy - state->y;
        float rz = wz - state->z;

        float proj = rx * dir_x + ry * dir_y + rz * dir_z;
        if (proj > 0.0f && proj <= stop_dist) {
            float px = rx - proj * dir_x;
            float py = ry - proj * dir_y;
            float pz = rz - proj * dir_z;
            float lateral_r = sqrtf(px * px + py * py + pz * pz);

            if (lateral_r < 1.1f) {
                return true;
            }
        }
    }
    return false;
}
