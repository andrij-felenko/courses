#include <math.h>

#define GYRO_LSB_PER_DPS   131.0f          /* MPU-6050, діапазон ±250 °/с */
#define DEG2RAD            (3.14159265f / 180.0f)

/* сирий 16-бітний відлік осі → кутова швидкість у рад/с */
static float gyro_rate_rad(int16_t raw)
{
    float dps = (float)raw / GYRO_LSB_PER_DPS;   /* °/с */
    return dps * DEG2RAD;                          /* рад/с */
}
