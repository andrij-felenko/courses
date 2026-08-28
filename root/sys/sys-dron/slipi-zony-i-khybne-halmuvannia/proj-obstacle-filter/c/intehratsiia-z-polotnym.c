#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define DISTANCE_SECTORS 72

/* Структура повідомлення PX4 uORB obstacle_distance */
typedef struct {
    uint64_t timestamp_us;
    uint16_t distances[DISTANCE_SECTORS]; /* Дистанція в сантиметрах, UINT16_MAX = немає перешкоди */
    uint16_t min_distance_cm;
    uint16_t max_distance_cm;
    uint8_t sensor_type;                  /* MAV_DISTANCE_SENSOR_LASER */
    float increment_deg;                  /* 5.0 градусів */
    float angle_offset_deg;               /* 0.0 */
    uint8_t frame;                        /* MAV_FRAME_BODY_FRD */
} ObstacleDistanceMsg;

void populate_obstacle_distance(const VoxelEntry* voxels, size_t n_voxels, 
                                const VehicleState* state, 
                                ObstacleDistanceMsg* msg, 
                                uint64_t now_us) {
    msg->timestamp_us = now_us;
    msg->min_distance_cm = 20;
    msg->max_distance_cm = 2000;
    msg->increment_deg = 360.0f / (float)DISTANCE_SECTORS;
    msg->angle_offset_deg = 0.0f;
    msg->sensor_type = 0; /* MAV_DISTANCE_SENSOR_LASER */
    msg->frame = 12;      /* MAV_FRAME_BODY_FRD */

    for (int i = 0; i < DISTANCE_SECTORS; ++i) {
        msg->distances[i] = UINT16_MAX;
    }

    for (size_t i = 0; i < n_voxels; ++i) {
        if (!voxels[i].occupied) continue;

        float wx = ((float)voxels[i].vx + 0.5f) * VOXEL_SIZE;
        float wy = ((float)voxels[i].vy + 0.5f) * VOXEL_SIZE;
        float wz = ((float)voxels[i].vz + 0.5f) * VOXEL_SIZE;

        float dx = wx - state->x;
        float dy = wy - state->y;
        float dz = wz - state->z;

        if (fabsf(dz) > 1.5f) continue; /* Фільтруємо об'єкти занадто вище/нижче площини польоту */

        float dist_m = sqrtf(dx * dx + dy * dy);
        if (dist_m < 0.2f || dist_m > 20.0f) continue;

        /* Кут у тілофіксованій системі FRD */
        float yaw_global = atan2f(dy, dx);
        float yaw_body = yaw_global - state->yaw;
        while (yaw_body < 0.0f) yaw_body += 2.0f * (float)M_PI;
        while (yaw_body >= 2.0f * (float)M_PI) yaw_body -= 2.0f * (float)M_PI;

        int sector = (int)floorf(yaw_body / (2.0f * (float)M_PI / (float)DISTANCE_SECTORS));
        if (sector >= 0 && sector < DISTANCE_SECTORS) {
            uint16_t dist_cm = (uint16_t)(dist_m * 100.0f);
            if (dist_cm < msg->distances[sector]) {
                msg->distances[sector] = dist_cm;
            }
        }
    }
}
