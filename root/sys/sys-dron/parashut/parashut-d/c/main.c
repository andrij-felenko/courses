#include <stdint.h>
#include <stdbool.h>
#include <math.h>

/* Порогові константи детектора аварій PTU */
#define PTU_FREEFALL_ACCEL_THRESH_G   0.22f   /* Поріг вільного падіння (|a| < 0.22g ≈ 2.15 м/с²) */
#define PTU_TUMBLE_GYRO_THRESH_DPS    380.0f  /* Поріг штопору (|omega| > 380 град/с) */
#define PTU_CONFIRM_TIME_MS           90      /* Час утримання аварійного стану для підтвердження */
#define PTU_MOTOR_SPINDOWN_DELAY_MS   50      /* Затримка зупинки гвинтів (FTS -> Eject) */
#define PTU_IGNITER_PULSE_DURATION_MS 200     /* Тривалість імпульсу струму підпалу піропатрона */
#define GRAVITY_MSS                   9.80665f

typedef enum {
    PTU_STATE_DISARMED = 0,
    PTU_STATE_ARMED,
    PTU_STATE_FREEFALL_CONFIRMING,
    PTU_STATE_TUMBLE_CONFIRMING,
    PTU_STATE_MOTOR_CUTOFF_ACTIVE,
    PTU_STATE_IGNITION_ACTIVE,
    PTU_STATE_DEPLOYED
} ptu_state_t;

typedef struct {
    float accel_x, accel_y, accel_z; /* м/с^2 */
    float gyro_x, gyro_y, gyro_z;    /* град/с */
} ptu_imu_raw_t;

typedef struct {
    ptu_state_t state;
    uint32_t state_entry_time_ms;
    uint32_t anomaly_start_time_ms;
    float filtered_accel_mag_g;
    float filtered_gyro_mag_dps;
    bool fts_engaged;
    bool igniter_fired;
} ptu_controller_t;

/* Апаратні абстракції (HAL виклики) */
extern void hal_fts_set_cutoff(bool disable_motors);
extern void hal_igniter_set_power(bool enable_current);
extern uint32_t hal_get_time_ms(void);

void ptu_init(ptu_controller_t *ptu) {
    ptu->state = PTU_STATE_DISARMED;
    ptu->state_entry_time_ms = hal_get_time_ms();
    ptu->anomaly_start_time_ms = 0;
    ptu->filtered_accel_mag_g = 1.0f;
    ptu->filtered_gyro_mag_dps = 0.0f;
    ptu->fts_engaged = false;
    ptu->igniter_fired = false;

    hal_fts_set_cutoff(false);
    hal_igniter_set_power(false);
}

void ptu_set_armed(ptu_controller_t *ptu, bool armed) {
    if (ptu->state == PTU_STATE_DEPLOYED || ptu->state >= PTU_STATE_MOTOR_CUTOFF_ACTIVE) {
        return; /* Заборона скидання статусу під час виконання порятунку */
    }
    ptu->state = armed ? PTU_STATE_ARMED : PTU_STATE_DISARMED;
    ptu->state_entry_time_ms = hal_get_time_ms();
}

void ptu_update(ptu_controller_t *ptu, const ptu_imu_raw_t *imu) {
    uint32_t now = hal_get_time_ms();

    /* 1. Обчислення модулів векторів прискорення та кутової швидкості */
    float a_mag_mss = sqrtf(imu->accel_x * imu->accel_x +
                            imu->accel_y * imu->accel_y +
                            imu->accel_z * imu->accel_z);
    float a_mag_g = a_mag_mss / GRAVITY_MSS;

    float w_mag_dps = sqrtf(imu->gyro_x * imu->gyro_x +
                            imu->gyro_y * imu->gyro_y +
                            imu->gyro_z * imu->gyro_z);

    /* 2. Експоненційний фільтр низьких частот (EMA, alpha = 0.3) для зрізання вібрацій */
    const float alpha = 0.30f;
    ptu->filtered_accel_mag_g = alpha * a_mag_g + (1.0f - alpha) * ptu->filtered_accel_mag_g;
    ptu->filtered_gyro_mag_dps = alpha * w_mag_dps + (1.0f - alpha) * ptu->filtered_gyro_mag_dps;

    bool is_freefall = (ptu->filtered_accel_mag_g < PTU_FREEFALL_ACCEL_THRESH_G);
    bool is_tumble = (ptu->filtered_gyro_mag_dps > PTU_TUMBLE_GYRO_THRESH_DPS);

    /* 3. Скінченний автомат станів безпеки */
    switch (ptu->state) {
        case PTU_STATE_DISARMED:
            /* На землі парашут заблокований від хибного відстрілу */
            break;

        case PTU_STATE_ARMED:
            if (is_freefall) {
                ptu->state = PTU_STATE_FREEFALL_CONFIRMING;
                ptu->anomaly_start_time_ms = now;
            } else if (is_tumble) {
                ptu->state = PTU_STATE_TUMBLE_CONFIRMING;
                ptu->anomaly_start_time_ms = now;
            }
            break;

        case PTU_STATE_FREEFALL_CONFIRMING:
            if (!is_freefall) {
                /* Короткочасний пілотажний маневр, скидання тривоги */
                ptu->state = PTU_STATE_ARMED;
            } else if ((now - ptu->anomaly_start_time_ms) >= PTU_CONFIRM_TIME_MS) {
                /* Вільне падіння підтверджено: перший крок - відсічка моторів */
                ptu->state = PTU_STATE_MOTOR_CUTOFF_ACTIVE;
                ptu->state_entry_time_ms = now;
                hal_fts_set_cutoff(true);
                ptu->fts_engaged = true;
            }
            break;

        case PTU_STATE_TUMBLE_CONFIRMING:
            if (!is_tumble) {
                ptu->state = PTU_STATE_ARMED;
            } else if ((now - ptu->anomaly_start_time_ms) >= PTU_CONFIRM_TIME_MS) {
                /* Некерований штопор підтверджено: відсічка моторів */
                ptu->state = PTU_STATE_MOTOR_CUTOFF_ACTIVE;
                ptu->state_entry_time_ms = now;
                hal_fts_set_cutoff(true);
                ptu->fts_engaged = true;
            }
            break;

        case PTU_STATE_MOTOR_CUTOFF_ACTIVE:
            /* Очікування повної зупинки лопатей (Cut Before Deploy) */
            if ((now - ptu->state_entry_time_ms) >= PTU_MOTOR_SPINDOWN_DELAY_MS) {
                ptu->state = PTU_STATE_IGNITION_ACTIVE;
                ptu->state_entry_time_ms = now;
                hal_igniter_set_power(true);
                ptu->igniter_fired = true;
            }
            break;

        case PTU_STATE_IGNITION_ACTIVE:
            /* Формування імпульсу струму на піропатрон */
            if ((now - ptu->state_entry_time_ms) >= PTU_IGNITER_PULSE_DURATION_MS) {
                hal_igniter_set_power(false);
                ptu->state = PTU_STATE_DEPLOYED;
                ptu->state_entry_time_ms = now;
            }
            break;

        case PTU_STATE_DEPLOYED:
            /* Парашут відстріляно, мотори залишаються знеструмленими до посадки */
            hal_fts_set_cutoff(true);
            break;
    }
}
