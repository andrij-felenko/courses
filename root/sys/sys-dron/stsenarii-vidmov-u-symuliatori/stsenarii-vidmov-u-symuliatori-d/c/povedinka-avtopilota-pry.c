#include <math.h>
#include <stdbool.h>
#include <stdint.h>

#define CHI2_3DOF_GATE_THRESHOLD    11.34f  // 99% довіри для 3D вектора
#define EKF_INNOVATION_TIMEOUT_US   1500000ULL

typedef struct {
    float x, y, z;
} vector3f_t;

typedef struct {
    float S[3][3];       // Коваріаційна матриця інновації 3x3
    float S_inv[3][3];   // Обернена матриця
    vector3f_t innov;    // Вектор нев'язки y = z - Hx
    uint64_t last_valid_time_us;
    bool gate_passed;
    bool navigation_lost;
} ekf_gate_checker_t;

// Обчислення оберненої матриці 3x3
static bool invert_matrix_3x3(const float m[3][3], float inv[3][3]) {
    float det = m[0][0]*(m[1][1]*m[2][2] - m[1][2]*m[2][1]) -
                m[0][1]*(m[1][0]*m[2][2] - m[1][2]*m[2][0]) +
                m[0][2]*(m[1][0]*m[2][1] - m[1][2]*m[2][0]);
    if (fabsf(det) < 1e-9f) return false;
    float invdet = 1.0f / det;

    inv[0][0] =  (m[1][1]*m[2][2] - m[1][2]*m[2][1]) * invdet;
    inv[0][1] = -(m[0][1]*m[2][2] - m[0][2]*m[2][1]) * invdet;
    inv[0][2] =  (m[0][1]*m[1][2] - m[0][2]*m[1][1]) * invdet;
    inv[1][0] = -(m[1][0]*m[2][2] - m[1][2]*m[2][0]) * invdet;
    inv[1][1] =  (m[0][0]*m[2][2] - m[0][2]*m[2][0]) * invdet;
    inv[1][2] = -(m[0][0]*m[1][2] - m[0][2]*m[1][0]) * invdet;
    inv[2][0] =  (m[1][0]*m[2][1] - m[1][2]*m[2][0]) * invdet;
    inv[2][1] = -(m[0][0]*m[2][1] - m[0][2]*m[2][0]) * invdet;
    inv[2][2] =  (m[0][0]*m[1][1] - m[0][1]*m[1][0]) * invdet;
    return true;
}

bool ekf_check_gnss_innovation(ekf_gate_checker_t *checker,
                               vector3f_t z_measurement,
                               vector3f_t predicted_state,
                               float cov_S[3][3],
                               uint64_t now_us) {
    checker->innov.x = z_measurement.x - predicted_state.x;
    checker->innov.y = z_measurement.y - predicted_state.y;
    checker->innov.z = z_measurement.z - predicted_state.z;

    for (int r = 0; r < 3; ++r)
        for (int c = 0; c < 3; ++c)
            checker->S[r][c] = cov_S[r][c];

    if (!invert_matrix_3x3(checker->S, checker->S_inv)) {
        checker->gate_passed = false;
        return false;
    }

    float y[3] = { checker->innov.x, checker->innov.y, checker->innov.z };
    float temp[3] = { 0.0f, 0.0f, 0.0f };

    for (int i = 0; i < 3; ++i) {
        for (int j = 0; j < 3; ++j) {
            temp[i] += y[j] * checker->S_inv[j][i];
        }
    }

    float nis = temp[0]*y[0] + temp[1]*y[1] + temp[2]*y[2];

    if (nis <= CHI2_3DOF_GATE_THRESHOLD) {
        checker->gate_passed = true;
        checker->last_valid_time_us = now_us;
        checker->navigation_lost = false;
        return true;
    } else {
        checker->gate_passed = false;
        if (now_us - checker->last_valid_time_us > EKF_INNOVATION_TIMEOUT_US) {
            checker->navigation_lost = true;
        }
        return false;
    }
}
