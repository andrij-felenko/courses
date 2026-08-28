#include <stdbool.h>
#include <stdint.h>
#include <math.h>

#define CRASH_ACCEL_THRESHOLD_G     15.0f   /* Поріг перевантаження (g) */
#define CRASH_GYRO_THRESHOLD_DPS    1200.0f /* Поріг кутової швидкості (град/с) */
#define CRASH_DEBOUNCE_SAMPLES      3       /* Кількість вибірок для підтвердження */

typedef struct {
    float ax_g;
    float ay_g;
    float az_g;
    float gx_dps;
    float gy_dps;
    float gz_dps;
} imu_sensor_data_t;

typedef struct {
    uint8_t impact_counter;
    bool is_crashed;
    bool disarm_latched;
} crash_detector_t;

void crash_detector_init(crash_detector_t *detector) {
    if (!detector) return;
    detector->impact_counter = 0;
    detector->is_crashed = false;
    detector->disarm_latched = false;
}

bool crash_detector_update(crash_detector_t *detector, 
                           const imu_sensor_data_t *imu,
                           bool is_armed) {
    if (!detector || !imu || !is_armed) {
        if (detector) detector->impact_counter = 0;
        return false;
    }

    if (detector->disarm_latched) {
        return true; /* Стан аварії зафіксовано до ручного скидання */
    }

    /* 1. Обчислення модуля сумарного лінійного перевантаження */
    float accel_sq = (imu->ax_g * imu->ax_g) + 
                     (imu->ay_g * imu->ay_g) + 
                     (imu->az_g * imu->az_g);
    float accel_mag = sqrtf(accel_sq);

    /* 2. Обчислення максимальної кутової швидкості */
    float gyro_max = fabsf(imu->gx_dps);
    if (fabsf(imu->gy_dps) > gyro_max) gyro_max = fabsf(imu->gy_dps);
    if (fabsf(imu->gz_dps) > gyro_max) gyro_max = fabsf(imu->gz_dps);

    /* 3. Критерій зіткнення: сильний удар або неконтрольоване обертання */
    bool condition_impact = (accel_mag >= CRASH_ACCEL_THRESHOLD_G);
    bool condition_spin = (gyro_max >= CRASH_GYRO_THRESHOLD_DPS);

    if (condition_impact || condition_spin) {
        if (detector->impact_counter < 255) {
            detector->impact_counter++;
        }
    } else {
        if (detector->impact_counter > 0) {
            detector->impact_counter--;
        }
    }

    /* 4. Спрацьовування захисту при досягненні лічильника */
    if (detector->impact_counter >= CRASH_DEBOUNCE_SAMPLES) {
        detector->is_crashed = true;
        detector->disarm_latched = true;
        return true;
    }

    return false;
}

void crash_detector_reset(crash_detector_t *detector) {
    if (!detector) return;
    detector->impact_counter = 0;
    detector->is_crashed = false;
    detector->disarm_latched = false;
}
