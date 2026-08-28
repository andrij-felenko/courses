#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <math.h>
#include <stdint.h>

#define MAX_POINTS 4096
#define MAX_VOXELS 16384
#define VOXEL_SIZE 0.2f       /* Розмір ребра вокселя 20 см */
#define HIT_INCREMENT 1
#define DECAY_PER_SEC 2.0f
#define OCCUPIED_THRESHOLD 3
#define MAX_WEIGHT 10

typedef struct {
    float x, y, z;
    float intensity;
} Point3D;

typedef struct {
    float x, y, z;
    float vx, vy, vz;
    float roll, pitch, yaw;
} DroneKinematics;

typedef struct {
    int32_t vx, vy, vz;
    float weight;
    float last_time;
} VoxelCell;

typedef struct {
    VoxelCell cells[MAX_VOXELS];
    size_t count;
} VoxelGrid;

/* Перетворення точки із системи координат сенсора у світову систему ENU */
Point3D transform_sensor_to_world(Point3D p, DroneKinematics k) {
    /* Спрощена матриця повороту R(yaw, pitch, roll) */
    float cy = cosf(k.yaw), sy = sinf(k.yaw);
    float cp = cosf(k.pitch), sp = sinf(k.pitch);
    float cr = cosf(k.roll), sr = sinf(k.roll);

    float r00 = cy * cp;
    float r01 = cy * sp * sr - sy * cr;
    float r02 = cy * sp * cr + sy * sr;

    float r10 = sy * cp;
    float r11 = sy * sp * sr + cy * cr;
    float r12 = sy * sp * cr - cy * sr;

    float r20 = -sp;
    float r21 = cp * sr;
    float r22 = cp * cr;

    Point3D world_p;
    world_p.x = k.x + (r00 * p.x + r01 * p.y + r02 * p.z);
    world_p.y = k.y + (r10 * p.x + r11 * p.y + r12 * p.z);
    world_p.z = k.z + (r20 * p.x + r21 * p.y + r22 * p.z);
    world_p.intensity = p.intensity;
    return world_p;
}

/* Оновлення воксельної сітки персистентності */
void update_persistence_grid(VoxelGrid* grid, const Point3D* points, size_t n_pts, float current_time) {
    /* Часове згасання існуючих комірок */
    for (size_t i = 0; i < grid->count; ++i) {
        float dt = current_time - grid->cells[i].last_time;
        if (dt > 0.05f) {
            grid->cells[i].weight -= DECAY_PER_SEC * dt;
            grid->cells[i].last_time = current_time;
            if (grid->cells[i].weight < 0.0f) grid->cells[i].weight = 0.0f;
        }
    }

    /* Інтеграція нових точок */
    for (size_t i = 0; i < n_pts; ++i) {
        int32_t ivx = (int32_t)floorf(points[i].x / VOXEL_SIZE);
        int32_t ivy = (int32_t)floorf(points[i].y / VOXEL_SIZE);
        int32_t ivz = (int32_t)floorf(points[i].z / VOXEL_SIZE);

        bool found = false;
        for (size_t j = 0; j < grid->count; ++j) {
            if (grid->cells[j].vx == ivx && grid->cells[j].vy == ivy && grid->cells[j].vz == ivz) {
                grid->cells[j].weight += HIT_INCREMENT;
                if (grid->cells[j].weight > MAX_WEIGHT) grid->cells[j].weight = MAX_WEIGHT;
                grid->cells[j].last_time = current_time;
                found = true;
                break;
            }
        }

        if (!found && grid->count < MAX_VOXELS) {
            grid->cells[grid->count].vx = ivx;
            grid->cells[grid->count].vy = ivy;
            grid->cells[grid->count].vz = ivz;
            grid->cells[grid->count].weight = HIT_INCREMENT;
            grid->cells[grid->count].last_time = current_time;
            grid->count++;
        }
    }
}

/* Перевірка загрози зіткнення вздовж коридору швидкості */
bool evaluate_collision_threat(const VoxelGrid* grid, DroneKinematics k, float a_max, float latency) {
    float speed = sqrtf(k.vx * k.vx + k.vy * k.vy + k.vz * k.vz);
    if (speed < 0.2f) return false;

    float stop_dist = (speed * speed) / (2.0f * a_max) + speed * latency + 1.0f;
    float dir_x = k.vx / speed;
    float dir_y = k.vy / speed;
    float dir_z = k.vz / speed;

    for (size_t i = 0; i < grid->count; ++i) {
        if (grid->cells[i].weight < OCCUPIED_THRESHOLD) continue;

        float wx = grid->cells[i].vx * VOXEL_SIZE + VOXEL_SIZE * 0.5f;
        float wy = grid->cells[i].vy * VOXEL_SIZE + VOXEL_SIZE * 0.5f;
        float wz = grid->cells[i].vz * VOXEL_SIZE + VOXEL_SIZE * 0.5f;

        float rel_x = wx - k.x;
        float rel_y = wy - k.y;
        float rel_z = wz - k.z;

        /* Проєкція на вектор швидкості */
        float proj = rel_x * dir_x + rel_y * dir_y + rel_z * dir_z;
        if (proj > 0.0f && proj <= stop_dist) {
            /* Відстань від осі руху */
            float perp_x = rel_x - proj * dir_x;
            float perp_y = rel_y - proj * dir_y;
            float perp_z = rel_z - proj * dir_z;
            float lateral_dist = sqrtf(perp_x * perp_x + perp_y * perp_y + perp_z * perp_z);

            if (lateral_dist < 1.2f) { /* Радіус коридору безпеки 1.2 м */
                return true; /* Зафіксовано підтверджену перешкоду в зоні гальмування */
            }
        }
    }
    return false;
}
