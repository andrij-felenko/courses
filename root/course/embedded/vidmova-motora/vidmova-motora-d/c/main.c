#include <stdint.h>
#include <stdbool.h>
#include <math.h>
#include <string.h>

#define MAX_ROTORS 8
#define FDI_CONFIRM_TICKS 20   /* 20 тиків по 2 мс = 40 мс фільтр */

typedef enum {
    FRAME_QUAD_X = 4,
    FRAME_HEXA_X = 6,
    FRAME_OCTO_X = 8
} FrameType;

typedef enum {
    MOTOR_OK = 0,
    MOTOR_SUSPECTED = 1,
    MOTOR_FAILED = 2
} RotorHealth;

typedef struct {
    float x;           /* координата X на рамі (м) */
    float y;           /* координата Y на рамі (м) */
    float dir;         /* +1.0 для CCW, -1.0 для CW */
    float c_tau;       /* відношення реактивного моменту до тяги */
} RotorGeometry;

typedef struct {
    RotorHealth health[MAX_ROTORS];
    uint16_t fault_counter[MAX_ROTORS];
    bool spin_recovery_active;
    float B[4][MAX_ROTORS];        /* геометрія керування 4xN */
    float W_inv[MAX_ROTORS];       /* ваги актуаторів (діагональ W^-1) */
    float M_alloc[MAX_ROTORS][4];  /* передрахована матриця розподілу */
} FaultTolerantMixer;

/* Ініціалізація матриці геометрії для квадро/гекса/октокоптера */
void mixer_init(FaultTolerantMixer *m, FrameType type, float arm_length, float c_tau) {
    memset(m, 0, sizeof(FaultTolerantMixer));
    const float d_angle = 2.0f * (float)M_PI / (float)type;
    const float start_angle = d_angle * 0.5f; /* конфігурація X */

    for (uint8_t i = 0; i < (uint8_t)type; i++) {
        float angle = start_angle + i * d_angle;
        float rx = arm_length * cosf(angle);
        float ry = arm_length * sinf(angle);
        float rdir = (i % 2 == 0) ? 1.0f : -1.0f; /* чергування CW / CCW */

        m->B[0][i] = -ry;          /* roll  = -y * F */
        m->B[1][i] = rx;           /* pitch =  x * F */
        m->B[2][i] = rdir * c_tau; /* yaw   = dir * c_tau * F */
        m->B[3][i] = 1.0f;         /* сумарна тяга */

        m->W_inv[i] = 1.0f;
        m->health[i] = MOTOR_OK;
    }
}

/* Інверсія симетричної матриці 4x4 методом аналітичних мінорів */
static bool invert_4x4(const float A[4][4], float inv[4][4]) {
    float m[16], invOut[16];
    for (int r = 0; r < 4; r++) {
        for (int c = 0; c < 4; c++) {
            m[r * 4 + c] = A[r][c];
        }
    }

    invOut[0] = m[5] * m[10] * m[15] - m[5] * m[11] * m[14] - m[9] * m[6] * m[15] +
                m[9] * m[7] * m[14] + m[13] * m[6] * m[11] - m[13] * m[7] * m[10];
    invOut[4] = -m[4] * m[10] * m[15] + m[4] * m[11] * m[14] + m[8] * m[6] * m[15] -
                m[8] * m[7] * m[14] - m[12] * m[6] * m[11] + m[12] * m[7] * m[10];
    invOut[8] = m[4] * m[9] * m[15] - m[4] * m[11] * m[13] - m[8] * m[5] * m[15] +
                m[8] * m[7] * m[13] + m[12] * m[5] * m[11] - m[12] * m[7] * m[9];
    invOut[12] = -m[4] * m[9] * m[14] + m[4] * m[10] * m[13] + m[8] * m[5] * m[14] -
                 m[8] * m[6] * m[13] - m[12] * m[5] * m[10] + m[12] * m[6] * m[9];

    float det = m[0] * invOut[0] + m[1] * invOut[4] + m[2] * invOut[8] + m[3] * invOut[12];
    if (fabsf(det) < 1e-7f) {
        return false;
    }

    invOut[1] = -m[1] * m[10] * m[15] + m[1] * m[11] * m[14] + m[9] * m[2] * m[15] -
                m[9] * m[3] * m[14] - m[13] * m[2] * m[11] + m[13] * m[3] * m[10];
    invOut[5] = m[0] * m[10] * m[15] - m[0] * m[11] * m[14] - m[8] * m[2] * m[15] +
                m[8] * m[3] * m[14] + m[12] * m[2] * m[11] - m[12] * m[3] * m[10];
    invOut[9] = -m[0] * m[9] * m[15] + m[0] * m[11] * m[13] + m[8] * m[1] * m[15] -
                m[8] * m[3] * m[13] - m[12] * m[1] * m[11] + m[12] * m[3] * m[9];
    invOut[13] = m[0] * m[9] * m[14] - m[0] * m[10] * m[13] - m[8] * m[1] * m[14] +
                 m[8] * m[2] * m[13] + m[12] * m[1] * m[10] - m[12] * m[2] * m[9];

    invOut[2] = m[1] * m[6] * m[15] - m[1] * m[7] * m[14] - m[5] * m[2] * m[15] +
                m[5] * m[3] * m[14] + m[13] * m[2] * m[7] - m[13] * m[3] * m[6];
    invOut[6] = -m[0] * m[6] * m[15] + m[0] * m[7] * m[14] + m[4] * m[2] * m[15] -
                m[4] * m[3] * m[14] - m[12] * m[2] * m[7] + m[12] * m[3] * m[6];
    invOut[10] = m[0] * m[5] * m[15] - m[0] * m[7] * m[13] - m[4] * m[1] * m[15] +
                 m[4] * m[3] * m[13] + m[12] * m[1] * m[7] - m[12] * m[3] * m[5];
    invOut[14] = -m[0] * m[5] * m[14] + m[0] * m[6] * m[13] + m[4] * m[1] * m[14] -
                 m[4] * m[2] * m[13] - m[12] * m[1] * m[6] + m[12] * m[2] * m[5];

    invOut[3] = -m[1] * m[6] * m[11] + m[1] * m[7] * m[10] + m[5] * m[2] * m[11] -
                m[5] * m[3] * m[10] - m[9] * m[2] * m[7] + m[9] * m[3] * m[6];
    invOut[7] = m[0] * m[6] * m[11] - m[0] * m[7] * m[10] - m[4] * m[2] * m[11] +
                m[4] * m[3] * m[10] + m[8] * m[2] * m[7] - m[8] * m[3] * m[6];
    invOut[11] = -m[0] * m[5] * m[11] + m[0] * m[7] * m[9] + m[4] * m[1] * m[11] -
                 m[4] * m[3] * m[9] - m[8] * m[1] * m[7] + m[8] * m[3] * m[5];
    invOut[15] = m[0] * m[5] * m[10] - m[0] * m[6] * m[9] - m[4] * m[1] * m[10] +
                 m[4] * m[2] * m[9] + m[8] * m[1] * m[6] - m[8] * m[2] * m[5];

    float invDet = 1.0f / det;
    for (int i = 0; i < 16; i++) {
        inv[i / 4][i % 4] = invOut[i] * invDet;
    }
    return true;
}

/* Перерахунок матриці зваженої псевдоінверсії M = W^-1 * B^T * (B * W^-1 * B^T)^-1 */
bool mixer_recalculate_wls(FaultTolerantMixer *m, uint8_t n_rotors) {
    float BW[4][MAX_ROTORS];
    for (int r = 0; r < 4; r++) {
        for (int c = 0; c < n_rotors; c++) {
            BW[r][c] = m->B[r][c] * m->W_inv[c];
        }
    }

    float BWB_T[4][4];
    memset(BWB_T, 0, sizeof(BWB_T));
    for (int r = 0; r < 4; r++) {
        for (int c = 0; c < 4; c++) {
            for (int k = 0; k < n_rotors; k++) {
                BWB_T[r][c] += BW[r][k] * m->B[c][k];
            }
        }
    }

    float inv_BWB_T[4][4];
    if (!invert_4x4(BWB_T, inv_BWB_T)) {
        return false;
    }

    for (int i = 0; i < n_rotors; i++) {
        for (int j = 0; j < 4; j++) {
            m->M_alloc[i][j] = 0.0f;
            for (int k = 0; k < 4; k++) {
                m->M_alloc[i][j] += BW[k][i] * inv_BWB_T[k][j];
            }
        }
    }
    return true;
}

/* Оновлення стану FDI на основі eRPM та струму ESC */
void mixer_fdi_update(FaultTolerantMixer *m, uint8_t n_rotors,
                      const float cmd_outputs[MAX_ROTORS],
                      const float erpm[MAX_ROTORS],
                      const float current_amps[MAX_ROTORS]) {
    for (uint8_t i = 0; i < n_rotors; i++) {
        bool fault_detected = false;

        /* Критерій 1: сигнал газу є, але мотор стоїть або відпав DShot */
        if (cmd_outputs[i] > 0.15f && erpm[i] < 100.0f) {
            fault_detected = true;
        }
        /* Критерій 2: пропелер відірвався (шалені оберти при нульовому струмі) */
        if (cmd_outputs[i] > 0.40f && erpm[i] > 15000.0f && current_amps[i] < 1.0f) {
            fault_detected = true;
        }

        if (fault_detected) {
            if (m->fault_counter[i] < FDI_CONFIRM_TICKS) {
                m->fault_counter[i]++;
                m->health[i] = MOTOR_SUSPECTED;
            } else if (m->health[i] != MOTOR_FAILED) {
                m->health[i] = MOTOR_FAILED;
                m->W_inv[i] = 0.0f; /* Обнуляємо вагу мотора */

                if (n_rotors == FRAME_QUAD_X) {
                    /* Для квадрокоптера активуємо режим швидкого аварійного обертання */
                    m->spin_recovery_active = true;
                } else {
                    /* Для гекса/октокоптера перераховуємо матрицю розподілу */
                    mixer_recalculate_wls(m, n_rotors);
                }
            }
        } else {
            if (m->fault_counter[i] > 0 && m->health[i] != MOTOR_FAILED) {
                m->fault_counter[i]--;
                if (m->fault_counter[i] == 0) {
                    m->health[i] = MOTOR_OK;
                }
            }
        }
    }
}

/* Обчислення виходів моторів у штатному режимі та режимі порятунку */
void mixer_compute(FaultTolerantMixer *m, uint8_t n_rotors,
                   float roll_cmd, float pitch_cmd, float yaw_cmd, float thrust_cmd,
                   float current_yaw_rad, float target_heading_rad,
                   float out_motor[MAX_ROTORS]) {
    if (m->spin_recovery_active && n_rotors == FRAME_QUAD_X) {
        /* Аварійний режим Single-Axis Spin Recovery для квадрокоптера */
        float cyclic_amp = 0.15f; /* амплітуда модуляції нахилу */
        float base_thrust = (thrust_cmd < 0.65f) ? thrust_cmd : 0.65f;

        for (uint8_t i = 0; i < n_rotors; i++) {
            if (m->health[i] == MOTOR_FAILED) {
                out_motor[i] = 0.0f;
            } else {
                /* Гармонійна модуляція тяги синхронно з кутом повороту */
                float rotor_azimuth = i * (float)M_PI_2;
                float phase = current_yaw_rad - target_heading_rad + rotor_azimuth;
                float cyclic = cyclic_amp * cosf(phase);
                float val = base_thrust + cyclic;

                /* Насичення виходу [0.0 ... 1.0] */
                if (val < 0.05f) val = 0.05f;
                if (val > 1.0f) val = 1.0f;
                out_motor[i] = val;
            }
        }
    } else {
        /* Класичне зважене мікшування для Hexa/Octo або штатного Quad */
        float v[4] = { roll_cmd, pitch_cmd, yaw_cmd, thrust_cmd };

        for (uint8_t i = 0; i < n_rotors; i++) {
            if (m->health[i] == MOTOR_FAILED) {
                out_motor[i] = 0.0f;
                continue;
            }
            float sum = 0.0f;
            for (int k = 0; k < 4; k++) {
                sum += m->M_alloc[i][k] * v[k];
            }
            if (sum < 0.0f) sum = 0.0f;
            if (sum > 1.0f) sum = 1.0f;
            out_motor[i] = sum;
        }
    }
}
