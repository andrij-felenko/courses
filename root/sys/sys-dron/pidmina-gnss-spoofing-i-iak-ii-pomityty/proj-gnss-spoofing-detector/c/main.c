#include <stdbool.h>
#include <stdint.h>
#include <math.h>
#include <string.h>

#define MAX_SATELLITES 16
#define IMU_BUFFER_SIZE 64

typedef enum {
    SPOOF_STATE_CLEAN = 0,
    SPOOF_STATE_DEGRADED = 1,
    SPOOF_STATE_CONFIRMED_SPOOF = 2
} SpoofState;

typedef struct {
    double x, y, z;
} Vec3;

typedef struct {
    uint8_t prn;
    double elevation_rad;
    double cno_dbhz;
    double doppler_mps;     /* Радіальна швидкість, виміряна за Доплером */
    Vec3 los_vector;        /* Одиничний вектор прямої видимості до супутника (ECEF) */
    Vec3 sat_velocity;      /* Вектор швидкості супутника (ECEF) */
    double pseudorange_m;
} SatObservation;

typedef struct {
    uint64_t timestamp_us;
    Vec3 velocity_ecef;     /* Інтегрована швидкість від бортового EKF/IMU */
    Vec3 accel_body;
} ImuStateSample;

typedef struct {
    /* Кільцевий буфер вимірювань IMU для вирівнювання затримки GNSS */
    ImuStateSample imu_history[IMU_BUFFER_SIZE];
    uint32_t imu_head;

    /* Поточні метрики загрози */
    double threat_score;
    double cno_anomaly_score;
    double doppler_residual_norm;
    double raim_sse_metric;

    SpoofState state;
    uint32_t consecutive_alarms;
} AntiSpoofDetector;

/* Ініціалізація детектора */
void anti_spoof_init(AntiSpoofDetector *det) {
    memset(det, 0, sizeof(AntiSpoofDetector));
    det->state = SPOOF_STATE_CLEAN;
}

/* Запис відліку IMU в кільцевий буфер */
void anti_spoof_push_imu(AntiSpoofDetector *det, uint64_t ts_us, Vec3 vel, Vec3 acc) {
    uint32_t idx = det->imu_head % IMU_BUFFER_SIZE;
    det->imu_history[idx].timestamp_us = ts_us;
    det->imu_history[idx].velocity_ecef = vel;
    det->imu_history[idx].accel_body = acc;
    det->imu_head++;
}

/* Пошук стану IMU, синхронізованого за часом із пакетом GNSS */
static bool get_synced_imu(const AntiSpoofDetector *det, uint64_t gnss_ts_us, Vec3 *out_vel) {
    if (det->imu_head == 0) return false;

    uint32_t count = (det->imu_head < IMU_BUFFER_SIZE) ? det->imu_head : IMU_BUFFER_SIZE;
    uint32_t best_idx = 0;
    int64_t min_dt = INT64_MAX;

    for (uint32_t i = 0; i < count; i++) {
        uint32_t idx = (det->imu_head - 1 - i) % IMU_BUFFER_SIZE;
        int64_t dt = llabs((int64_t)det->imu_history[idx].timestamp_us - (int64_t)gnss_ts_us);
        if (dt < min_dt) {
            min_dt = dt;
            best_idx = idx;
        }
    }

    /* Допуск синхронізації не більше 50 мс */
    if (min_dt > 50000) return false;

    *out_vel = det->imu_history[best_idx].velocity_ecef;
    return true;
}

static inline double vec3_dot(Vec3 a, Vec3 b) {
    return a.x * b.x + a.y * b.y + a.z * b.z;
}

/* 1. Аналізатор енергетичного профілю C/N0 */
static double evaluate_cno_profile(const SatObservation *sats, uint32_t num_sats) {
    if (num_sats < 4) return 0.0;

    double mean_cno = 0.0;
    double sum_sq_diff = 0.0;
    uint32_t low_elev_high_cno_count = 0;

    for (uint32_t i = 0; i < num_sats; i++) {
        mean_cno += sats[i].cno_dbhz;
        /* Аномалія: низький супутник (<20 град) з неприродною потужністю (>48 дБ-Гц) */
        if (sats[i].elevation_rad < (20.0 * M_PI / 180.0) && sats[i].cno_dbhz > 48.0) {
            low_elev_high_cno_count++;
        }
    }
    mean_cno /= num_sats;

    for (uint32_t i = 0; i < num_sats; i++) {
        double diff = sats[i].cno_dbhz - mean_cno;
        sum_sq_diff += diff * diff;
    }
    double variance = sum_sq_diff / num_sats;

    double score = 0.0;
    /* Неприродно плаский спектр потужності від єдиного передавача */
    if (variance < 0.45 && mean_cno > 46.0) {
        score += 0.6;
    }
    score += (double)low_elev_high_cno_count * 0.25;
    return (score > 1.0) ? 1.0 : score;
}

/* 2. Доплерівсько-інерціальний крос-чек */
static double evaluate_doppler_consistency(const SatObservation *sats, uint32_t num_sats,
                                          Vec3 imu_vel, double *out_max_residual) {
    if (num_sats < 4) return 0.0;

    double max_res = 0.0;
    double sum_sq_res = 0.0;

    for (uint32_t i = 0; i < num_sats; i++) {
        Vec3 rel_vel;
        rel_vel.x = sats[i].sat_velocity.x - imu_vel.x;
        rel_vel.y = sats[i].sat_velocity.y - imu_vel.y;
        rel_vel.z = sats[i].sat_velocity.z - imu_vel.z;

        double expected_doppler_mps = vec3_dot(rel_vel, sats[i].los_vector);
        double res = fabs(sats[i].doppler_mps - expected_doppler_mps);

        if (res > max_res) max_res = res;
        sum_sq_res += res * res;
    }

    *out_max_residual = max_res;
    double rms_res = sqrt(sum_sq_res / num_sats);

    /* Поріг відхилення швидкості: шум понад 1.5 м/с сигналізує про спуфінг */
    if (rms_res < 0.6) return 0.0;
    if (rms_res > 2.5) return 1.0;
    return (rms_res - 0.6) / (2.5 - 0.6);
}

/* Основний цикл обробки епохи GNSS */
SpoofState anti_spoof_update(AntiSpoofDetector *det, uint64_t gnss_ts_us,
                             const SatObservation *sats, uint32_t num_sats) {
    if (num_sats < 4) {
        det->state = SPOOF_STATE_DEGRADED;
        return det->state;
    }

    Vec3 synced_imu_vel;
    bool has_imu = get_synced_imu(det, gnss_ts_us, &synced_imu_vel);

    /* Обчислення компонентів загрози */
    det->cno_anomaly_score = evaluate_cno_profile(sats, num_sats);

    double max_dopp_res = 0.0;
    double doppler_score = 0.0;
    if (has_imu) {
        doppler_score = evaluate_doppler_consistency(sats, num_sats, synced_imu_vel, &max_dopp_res);
    }
    det->doppler_residual_norm = max_dopp_res;

    /* Комплексна миттєва оцінка загрози (зважена сума) */
    double instant_threat = 0.35 * det->cno_anomaly_score + 0.65 * doppler_score;

    /* Інтегрування оцінки загрози фільтром першого порядку (α = 0.25) */
    det->threat_score = 0.75 * det->threat_score + 0.25 * instant_threat;

    /* Гістерезисний автомат переходів станів */
    if (det->threat_score > 0.65) {
        det->consecutive_alarms++;
        if (det->consecutive_alarms >= 3) {
            det->state = SPOOF_STATE_CONFIRMED_SPOOF;
        } else {
            det->state = SPOOF_STATE_DEGRADED;
        }
    } else if (det->threat_score < 0.25) {
        det->consecutive_alarms = 0;
        det->state = SPOOF_STATE_CLEAN;
    }

    return det->state;
}
