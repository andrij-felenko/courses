#include <stdint.h>
#include <stdbool.h>
#include <math.h>
#include <string.h>

#define MAX_ACTUATORS 8
#define FDI_RPM_TIMEOUT_MS 80
#define FDI_RESIDUAL_THRESH 12.5f /* рад/с² */

typedef struct {
    float roll;
    float pitch;
    float yaw;
    float thrust;
} ControlTorque;

typedef struct {
    float rpm;
    float current;
    float temperature;
    uint32_t last_update_ms;
    uint8_t error_flags;
} EscTelemetry;

typedef struct {
    uint8_t actuator_count;
    float inertia[3];          /* Головні моменти інерції Jx, Jy, Jz */
    float B_moment[3][MAX_ACTUATORS]; /* Моментні стовпці матриці B */
    uint8_t failed_mask;       /* Бітова маска несправних моторів */
    bool yaw_relaxed;          /* Прапорець релаксації осі рискання */
    float residual_acc[3];     /* Накопичена нев'язка спостерігача */
} FaultToleranceManager;

void fdi_init(FaultToleranceManager *mgr, uint8_t count, const float J[3], const float B_mom[3][MAX_ACTUATORS]) {
    mgr->actuator_count = count;
    mgr->inertia[0] = J[0];
    mgr->inertia[1] = J[1];
    mgr->inertia[2] = J[2];
    mgr->failed_mask = 0;
    mgr->yaw_relaxed = false;
    mgr->residual_acc[0] = 0.0f;
    mgr->residual_acc[1] = 0.0f;
    mgr->residual_acc[2] = 0.0f;
    memcpy(mgr->B_moment, B_mom, sizeof(mgr->B_moment));
}

uint8_t fdi_update(FaultToleranceManager *mgr,
                   const float gyro[3],
                   const float gyro_prev[3],
                   float dt,
                   const float actuator_cmd[MAX_ACTUATORS],
                   const EscTelemetry telemetry[MAX_ACTUATORS],
                   uint32_t now_ms) {
    if (dt <= 0.0001f) return mgr->failed_mask;

    /* 1. Обчислення виміряного кутового прискорення */
    float alpha_meas[3];
    for (int i = 0; i < 3; i++) {
        alpha_meas[i] = (gyro[i] - gyro_prev[i]) / dt;
    }

    /* 2. Модельне прискорення від команд: alpha_model = J⁻¹ * (B_M * u - w x Jw) */
    float gyro_cross_Jw[3];
    gyro_cross_Jw[0] = (mgr->inertia[2] - mgr->inertia[1]) * gyro[1] * gyro[2];
    gyro_cross_Jw[1] = (mgr->inertia[0] - mgr->inertia[2]) * gyro[0] * gyro[2];
    gyro_cross_Jw[2] = (mgr->inertia[1] - mgr->inertia[0]) * gyro[0] * gyro[1];

    float expected_moment[3] = {0.0f, 0.0f, 0.0f};
    for (int ax = 0; ax < 3; ax++) {
        for (int i = 0; i < mgr->actuator_count; i++) {
            if (!(mgr->failed_mask & (1 << i))) {
                expected_moment[ax] += mgr->B_moment[ax][i] * actuator_cmd[i];
            }
        }
    }

    float alpha_model[3];
    for (int i = 0; i < 3; i++) {
        alpha_model[i] = (expected_moment[i] - gyro_cross_Jw[i]) / mgr->inertia[i];
        /* Вектор нев'язки r(t) */
        float r = alpha_meas[i] - alpha_model[i];
        mgr->residual_acc[i] = 0.85f * mgr->residual_acc[i] + 0.15f * r;
    }

    /* 3. Апаратна діагностика через DShot телеметрію */
    for (uint8_t i = 0; i < mgr->actuator_count; i++) {
        if (mgr->failed_mask & (1 << i)) continue;

        bool cmd_active = (actuator_cmd[i] > 0.15f);
        bool rpm_zero = (telemetry[i].rpm < 50.0f);
        bool timed_out = (now_ms - telemetry[i].last_update_ms > FDI_RPM_TIMEOUT_MS);

        if ((cmd_active && rpm_zero) || timed_out || (telemetry[i].error_flags & 0x01)) {
            mgr->failed_mask |= (1 << i);
        }
    }

    /* 4. Ізоляція відмови за напрямком вектора нев'язки */
    float res_norm = sqrtf(mgr->residual_acc[0] * mgr->residual_acc[0] +
                           mgr->residual_acc[1] * mgr->residual_acc[1] +
                           mgr->residual_acc[2] * mgr->residual_acc[2]);

    if (res_norm > FDI_RESIDUAL_THRESH) {
        int best_motor = -1;
        float best_correlation = -1.0f;

        for (uint8_t i = 0; i < mgr->actuator_count; i++) {
            if (mgr->failed_mask & (1 << i)) continue;

            /* Очікуваний вектор втрати моменту: -B_M[:, i] * u_i / J */
            float def_vec[3];
            float def_norm_sq = 0.0f;
            for (int ax = 0; ax < 3; ax++) {
                def_vec[ax] = -mgr->B_moment[ax][i] * actuator_cmd[i] / mgr->inertia[ax];
                def_norm_sq += def_vec[ax] * def_vec[ax];
            }
            float def_norm = sqrtf(def_norm_sq);
            if (def_norm < 0.001f) continue;

            float dot = (mgr->residual_acc[0] * def_vec[0] +
                         mgr->residual_acc[1] * def_vec[1] +
                         mgr->residual_acc[2] * def_vec[2]) / (res_norm * def_norm);

            if (dot > best_correlation && dot > 0.75f) {
                best_correlation = dot;
                best_motor = i;
            }
        }

        if (best_motor >= 0) {
            mgr->failed_mask |= (1 << best_motor);
        }
    }

    /* Перевірка потреби релаксації рискання для 6-моторних схем */
    if (mgr->actuator_count == 6 && mgr->failed_mask != 0) {
        mgr->yaw_relaxed = true;
    }

    return mgr->failed_mask;
}
