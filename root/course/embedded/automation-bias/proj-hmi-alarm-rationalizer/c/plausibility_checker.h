#ifndef PLAUSIBILITY_CHECKER_H
#define PLAUSIBILITY_CHECKER_H

#include "alarm_rationalizer.h"
#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    PLAUSIBILITY_VALID = 0,     /* Дані узгоджені з фізичною моделлю, висока довіра */
    PLAUSIBILITY_DEGRADED,      /* Підвищена дисперсія шуму, помірна невизначеність */
    PLAUSIBILITY_SUSPECT,       /* Суттєва нев'язка між датчиками, потрібна увага оператора */
    PLAUSIBILITY_FAILED         /* Фізична неможливість, відмова сенсора чи алгоритму */
} PlausibilityStatus_t;

/**
 * @brief Оцінка сенсорного сигналу з довірчим інтервалом для HMI.
 */
typedef struct {
    float estimated_value;      /* Оцінене центральне значення фізичної величини */
    float confidence_bound_95;  /* Довірчий інтервал 95% (+/- 1.96 * sigma) */
    float variance;             /* Дисперсія похибки оцінки */
    float residual;             /* Нев'язка (відхилення вимірювання від моделі) */
    float confidence_score;     /* Метрика достовірності від 0.0 (недостовірно) до 1.0 (ідеально) */
    PlausibilityStatus_t status;
    uint32_t sample_count;
} SensorConfidenceEstimate_t;

/**
 * @brief Модуль перевірки фізичної достовірності (Truth-Maintenance Engine).
 */
typedef struct {
    float max_allowed_accel_jerk;
    float max_kinematic_residual;
    float max_power_residual_w;
    float min_confidence_alarm_threshold;
    uint16_t diagnostic_alarm_id;
} PlausibilityCheckerConfig_t;

typedef struct {
    PlausibilityCheckerConfig_t config;
    SensorConfidenceEstimate_t battery_confidence;
    SensorConfidenceEstimate_t nav_velocity_confidence;
    SensorConfidenceEstimate_t attitude_confidence;
    
    /* Внутрішній стан моделі для інтегрування */
    float last_imu_accel_x;
    float last_gnss_vel_x;
    uint64_t last_eval_time_ms;
} PlausibilityChecker_t;

/**
 * @brief Ініціалізація валідатора достовірності.
 */
void plausibility_checker_init(PlausibilityChecker_t *pc, const PlausibilityCheckerConfig_t *cfg);

/**
 * @brief Крос-валідація потрійно-резервованого датчика (2-out-of-3 voting з аналізом дисперсії).
 */
SensorConfidenceEstimate_t plausibility_eval_triple_sensor(float s1, float s2, float s3, float noise_sigma, float max_spread);

/**
 * @brief Перевірка кінематичної достовірності (узгодженість прискорення IMU та швидкості GNSS).
 */
void plausibility_check_kinematics(PlausibilityChecker_t *pc, float imu_accel_x, float gnss_vel_x, uint64_t now_ms);

/**
 * @brief Перевірка енергетичного балансу (напруга * струм проти механічної потужності моторів).
 */
void plausibility_check_battery_power(PlausibilityChecker_t *pc, float voltage, float current, float expected_power_w, uint64_t now_ms);

/**
 * @brief Синхронізація результатів достовірності з диспетчером тривог ISA-18.2.
 */
void plausibility_sync_to_rationalizer(PlausibilityChecker_t *pc, AlarmRationalizer_t *ar, uint64_t now_ms);

#ifdef __cplusplus
}
#endif

#endif /* PLAUSIBILITY_CHECKER_H */
