#include "plausibility_checker.h"
#include <math.h>
#include <string.h>

#ifndef fminf
#define fminf(a,b) ((a) < (b) ? (a) : (b))
#endif
#ifndef fmaxf
#define fmaxf(a,b) ((a) > (b) ? (a) : (b))
#endif

void plausibility_checker_init(PlausibilityChecker_t *pc, const PlausibilityCheckerConfig_t *cfg) {
    if (!pc) return;
    memset(pc, 0, sizeof(PlausibilityChecker_t));
    if (cfg) {
        memcpy(&pc->config, cfg, sizeof(PlausibilityCheckerConfig_t));
    }
}

SensorConfidenceEstimate_t plausibility_eval_triple_sensor(float s1, float s2, float s3, float noise_sigma, float max_spread) {
    SensorConfidenceEstimate_t est;
    memset(&est, 0, sizeof(est));

    /* Медіанне сортування 3 значень */
    float a = s1, b = s2, c = s3;
    if (a > b) { float t = a; a = b; b = t; }
    if (b > c) { float t = b; b = c; c = t; }
    if (a > b) { float t = a; a = b; b = t; }
    float median = b;

    float d12 = fabsf(s1 - s2);
    float d23 = fabsf(s2 - s3);
    float d31 = fabsf(s3 - s1);
    float max_diff = fmaxf(d12, fmaxf(d23, d31));

    est.estimated_value = median;
    est.residual = max_diff;

    if (max_diff <= max_spread) {
        /* Усі три датчики узгоджені */
        est.variance = (noise_sigma * noise_sigma) / 3.0f;
        est.confidence_bound_95 = 1.96f * sqrtf(est.variance);
        est.confidence_score = fmaxf(0.0f, 1.0f - (max_diff / (max_spread * 2.0f)));
        est.status = PLAUSIBILITY_VALID;
    } else if (d12 <= max_spread || d23 <= max_spread || d31 <= max_spread) {
        /* Один датчик вилетів (2-out-of-3 quorum) */
        est.variance = (noise_sigma * noise_sigma) / 2.0f;
        est.confidence_bound_95 = 1.96f * sqrtf(est.variance);
        est.confidence_score = 0.65f;
        est.status = PLAUSIBILITY_DEGRADED;
    } else {
        /* Усі 3 датчики показують різні значення (розбіжність) */
        est.variance = noise_sigma * noise_sigma * 4.0f;
        est.confidence_bound_95 = 1.96f * sqrtf(est.variance);
        est.confidence_score = 0.15f;
        est.status = PLAUSIBILITY_FAILED;
    }

    return est;
}

void plausibility_check_kinematics(PlausibilityChecker_t *pc, float imu_accel_x, float gnss_vel_x, uint64_t now_ms) {
    if (!pc) return;

    if (pc->last_eval_time_ms == 0) {
        pc->last_eval_time_ms = now_ms;
        pc->last_imu_accel_x = imu_accel_x;
        pc->last_gnss_vel_x = gnss_vel_x;
        pc->nav_velocity_confidence.estimated_value = gnss_vel_x;
        pc->nav_velocity_confidence.confidence_score = 1.0f;
        pc->nav_velocity_confidence.status = PLAUSIBILITY_VALID;
        return;
    }

    float dt = (float)(now_ms - pc->last_eval_time_ms) / 1000.0f;
    if (dt <= 0.0001f) return;

    /* Обчислення похідної швидкості за GNSS */
    float gnss_accel_x = (gnss_vel_x - pc->last_gnss_vel_x) / dt;
    float residual = fabsf(gnss_accel_x - imu_accel_x);

    pc->nav_velocity_confidence.estimated_value = gnss_vel_x;
    pc->nav_velocity_confidence.residual = residual;
    pc->nav_velocity_confidence.variance = residual * 0.25f + 0.05f;
    pc->nav_velocity_confidence.confidence_bound_95 = 1.96f * sqrtf(pc->nav_velocity_confidence.variance);

    if (residual < pc->config.max_kinematic_residual * 0.5f) {
        pc->nav_velocity_confidence.status = PLAUSIBILITY_VALID;
        pc->nav_velocity_confidence.confidence_score = 0.95f;
    } else if (residual < pc->config.max_kinematic_residual) {
        pc->nav_velocity_confidence.status = PLAUSIBILITY_DEGRADED;
        pc->nav_velocity_confidence.confidence_score = 0.70f;
    } else if (residual < pc->config.max_kinematic_residual * 2.0f) {
        pc->nav_velocity_confidence.status = PLAUSIBILITY_SUSPECT;
        pc->nav_velocity_confidence.confidence_score = 0.35f;
    } else {
        pc->nav_velocity_confidence.status = PLAUSIBILITY_FAILED;
        pc->nav_velocity_confidence.confidence_score = 0.05f;
    }

    pc->last_eval_time_ms = now_ms;
    pc->last_imu_accel_x = imu_accel_x;
    pc->last_gnss_vel_x = gnss_vel_x;
}

void plausibility_check_battery_power(PlausibilityChecker_t *pc, float voltage, float current, float expected_power_w, uint64_t now_ms) {
    if (!pc) return;
    (void)now_ms;

    float measured_power_w = voltage * current;
    float power_residual = fabsf(measured_power_w - expected_power_w);

    pc->battery_confidence.estimated_value = voltage;
    pc->battery_confidence.residual = power_residual;
    pc->battery_confidence.variance = (power_residual / 50.0f) * 0.1f + 0.02f;
    pc->battery_confidence.confidence_bound_95 = 1.96f * sqrtf(pc->battery_confidence.variance);

    if (power_residual <= pc->config.max_power_residual_w * 0.5f) {
        pc->battery_confidence.status = PLAUSIBILITY_VALID;
        pc->battery_confidence.confidence_score = 0.98f;
    } else if (power_residual <= pc->config.max_power_residual_w) {
        pc->battery_confidence.status = PLAUSIBILITY_DEGRADED;
        pc->battery_confidence.confidence_score = 0.75f;
    } else if (power_residual <= pc->config.max_power_residual_w * 2.0f) {
        pc->battery_confidence.status = PLAUSIBILITY_SUSPECT;
        pc->battery_confidence.confidence_score = 0.40f;
    } else {
        pc->battery_confidence.status = PLAUSIBILITY_FAILED;
        pc->battery_confidence.confidence_score = 0.05f;
    }
}

void plausibility_sync_to_rationalizer(PlausibilityChecker_t *pc, AlarmRationalizer_t *ar, uint64_t now_ms) {
    if (!pc || !ar) return;

    /* Обчислення мінімальної достовірності по системі */
    float min_conf = fminf(pc->nav_velocity_confidence.confidence_score, pc->battery_confidence.confidence_score);

    /* Передача інвертованого показника як входу для діагностичної тривоги ISA-18.2 */
    if (pc->config.diagnostic_alarm_id < ar->count) {
        alarm_rationalizer_update_value(ar, pc->config.diagnostic_alarm_id, min_conf, now_ms);
    }
}
