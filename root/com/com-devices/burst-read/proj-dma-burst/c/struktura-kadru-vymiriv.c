#include <stdint.h>

#pragma pack(push, 1)
typedef struct {
    uint8_t  status;
    int16_t  gyro_x;
    int16_t  gyro_y;
    int16_t  gyro_z;
    int16_t  accel_x;
    int16_t  accel_y;
    int16_t  accel_z;
    int16_t  temperature;
} imu_raw_frame_t;
#pragma pack(pop)
