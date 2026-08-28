#include <cstdint>

namespace sensor {

struct [[gnu::packed]] RawImuData {
    uint8_t  status;
    int16_t  gyro_x;
    int16_t  gyro_y;
    int16_t  gyro_z;
    int16_t  accel_x;
    int16_t  accel_y;
    int16_t  accel_z;
    int16_t  temperature;
};

} // namespace sensor
