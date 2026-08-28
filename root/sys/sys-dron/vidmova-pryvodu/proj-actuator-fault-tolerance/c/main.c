#include <stdint.h>
#include <stdbool.h>
#include <math.h>
#include <string.h>

#define ALLOC_MAX_ACTUATORS 8
#define ALLOC_AXES 4 /* 0: Thrust_Z, 1: Roll_X, 2: Pitch_Y, 3: Yaw_Z */
#define TIKHONOV_DAMPING 0.0001f

typedef struct {
    uint8_t num_actuators;
    float B[ALLOC_AXES][ALLOC_MAX_ACTUATORS];     /* Пряма матриця ефективності */
    float B_pinv[ALLOC_MAX_ACTUATORS][ALLOC_AXES];/* Зважена псевдообернена матриця */
    float weights[ALLOC_MAX_ACTUATORS];           /* Ваги приводів W_i */
    uint8_t fault_mask;                           /* Бітова маска несправних моторів */
    bool is_yaw_relaxed;                          /* Режим відключення каналу Yaw */
    float u_min[ALLOC_MAX_ACTUATORS];             /* Нижня межа сигналу привода */
    float u_max[ALLOC_MAX_ACTUATORS];             /* Верхня межа сигналу привода */
    float slew_rate_max;                          /* Максимальна швидкість наростання (1/с) */
    float u_prev[ALLOC_MAX_ACTUATORS];            /* Попередній вихідний сигнал */
} DynamicMixerAllocator;

/* Чисельно стабільна інверсія матриці 4x4 методом Гаусса-Жордана з вибором головного елемента */
static bool invert_matrix_4x4(const float A[4][4], float A_inv[4][4]) {
    float m[4][8];
    for (int i = 0; i < 4; i++) {
        for (int j = 0; j < 4; j++) m[i][j] = A[i][j];
        for (int j = 4; j < 8; j++) m[i][j] = (i == (j - 4)) ? 1.0f : 0.0f;
    }

    for (int i = 0; i < 4; i++) {
        int pivot = i;
        float max_val = fabsf(m[i][i]);
        for (int k = i + 1; k < 4; k++) {
            if (fabsf(m[k][i]) > max_val) {
                max_val = fabsf(m[k][i]);
                pivot = k;
            }
        }
        if (max_val < 1e-7f) return false; /* Матриця сингулярна */

        if (pivot != i) {
            for (int j = 0; j < 8; j++) {
                float tmp = m[i][j];
                m[i][j] = m[pivot][j];
                m[pivot][j] = tmp;
            }
        }

        float pivot_val = m[i][i];
        for (int j = 0; j < 8; j++) m[i][j] /= pivot_val;

        for (int k = 0; k < 4; k++) {
            if (k != i) {
                float factor = m[k][i];
                for (int j = 0; j < 8; j++) {
                    m[k][j] -= factor * m[i][j];
                }
            }
        }
    }

    for (int i = 0; i < 4; i++) {
        for (int j = 0; j < 4; j++) {
            A_inv[i][j] = m[i][j + 4];
        }
    }
    return true;
}

void allocator_init(DynamicMixerAllocator *alloc,
                    uint8_t num_actuators,
                    const float B_matrix[ALLOC_AXES][ALLOC_MAX_ACTUATORS],
                    float slew_rate) {
    alloc->num_actuators = (num_actuators > ALLOC_MAX_ACTUATORS) ? ALLOC_MAX_ACTUATORS : num_actuators;
    alloc->fault_mask = 0;
    alloc->is_yaw_relaxed = false;
    alloc->slew_rate_max = (slew_rate > 0.0f) ? slew_rate : 20.0f; /* 20 одиниць/с за замовчуванням */

    for (int ax = 0; ax < ALLOC_AXES; ax++) {
        for (int i = 0; i < alloc->num_actuators; i++) {
            alloc->B[ax][i] = B_matrix[ax][i];
        }
    }

    for (int i = 0; i < alloc->num_actuators; i++) {
        alloc->weights[i] = 1.0f;
        alloc->u_min[i] = 0.0f;
        alloc->u_max[i] = 1.0f;
        alloc->u_prev[i] = 0.0f;
    }

    allocator_recompute_pinv(alloc);
}

bool allocator_recompute_pinv(DynamicMixerAllocator *alloc) {
    /* 1. Побудова зваженої матриці Грама G = B * W⁻¹ * Bᵀ */
    float G[4][4] = {0};

    for (int ax1 = 0; ax1 < ALLOC_AXES; ax1++) {
        for (int ax2 = 0; ax2 < ALLOC_AXES; ax2++) {
            float sum = 0.0f;
            for (int i = 0; i < alloc->num_actuators; i++) {
                if (!(alloc->fault_mask & (1 << i))) {
                    float inv_w = 1.0f / alloc->weights[i];
                    sum += alloc->B[ax1][i] * inv_w * alloc->B[ax2][i];
                }
            }
            G[ax1][ax2] = sum;
        }
    }

    /* Якщо активний режим релаксації рискання, виключаємо вісь Yaw */
    if (alloc->is_yaw_relaxed) {
        G[3][0] = 0.0f; G[3][1] = 0.0f; G[3][2] = 0.0f;
        G[0][3] = 0.0f; G[1][3] = 0.0f; G[2][3] = 0.0f;
        G[3][3] = 1.0f;
    }

    /* Демпфування Тихонова */
    for (int ax = 0; ax < ALLOC_AXES; ax++) {
        G[ax][ax] += TIKHONOV_DAMPING;
    }

    /* 2. Обернення матриці G⁻¹ */
    float G_inv[4][4];
    if (!invert_matrix_4x4(G, G_inv)) {
        return false;
    }

    /* 3. B_pinv = W⁻¹ * Bᵀ * G⁻¹ */
    for (int i = 0; i < alloc->num_actuators; i++) {
        if (alloc->fault_mask & (1 << i)) {
            for (int ax = 0; ax < ALLOC_AXES; ax++) {
                alloc->B_pinv[i][ax] = 0.0f;
            }
        } else {
            float inv_w = 1.0f / alloc->weights[i];
            for (int ax = 0; ax < ALLOC_AXES; ax++) {
                float sum = 0.0f;
                for (int k = 0; k < ALLOC_AXES; k++) {
                    sum += alloc->B[k][i] * G_inv[k][ax];
                }
                alloc->B_pinv[i][ax] = inv_w * sum;
            }
        }
    }
    return true;
}

void allocator_set_fault_mask(DynamicMixerAllocator *alloc, uint8_t mask, bool relax_yaw) {
    if (alloc->fault_mask != mask || alloc->is_yaw_relaxed != relax_yaw) {
        alloc->fault_mask = mask;
        alloc->is_yaw_relaxed = relax_yaw;
        allocator_recompute_pinv(alloc);
    }
}

void allocator_allocate(DynamicMixerAllocator *alloc,
                        const float tau_des[ALLOC_AXES],
                        float dt,
                        float u_out[ALLOC_MAX_ACTUATORS]) {
    float tau[ALLOC_AXES];
    tau[0] = tau_des[0];
    tau[1] = tau_des[1];
    tau[2] = tau_des[2];
    tau[3] = alloc->is_yaw_relaxed ? 0.0f : tau_des[3];

    float raw_u[ALLOC_MAX_ACTUATORS];

    /* 1. Лінійний розподіл керування */
    for (int i = 0; i < alloc->num_actuators; i++) {
        if (alloc->fault_mask & (1 << i)) {
            raw_u[i] = 0.0f;
            continue;
        }

        float cmd = 0.0f;
        for (int ax = 0; ax < ALLOC_AXES; ax++) {
            cmd += alloc->B_pinv[i][ax] * tau[ax];
        }
        raw_u[i] = cmd;
    }

    /* 2. Пріоритетна десатурація та Slew Rate фільтрація */
    float max_slew = alloc->slew_rate_max * dt;

    for (int i = 0; i < alloc->num_actuators; i++) {
        if (alloc->fault_mask & (1 << i)) {
            u_out[i] = 0.0f;
            alloc->u_prev[i] = 0.0f;
            continue;
        }

        /* Обмеження діапазону */
        float clamped = raw_u[i];
        if (clamped < alloc->u_min[i]) clamped = alloc->u_min[i];
        if (clamped > alloc->u_max[i]) clamped = alloc->u_max[i];

        /* Фільтр швидкості наростання сигналу */
        if (dt > 0.0001f) {
            float delta = clamped - alloc->u_prev[i];
            if (delta > max_slew) clamped = alloc->u_prev[i] + max_slew;
            if (delta < -max_slew) clamped = alloc->u_prev[i] - max_slew;
        }

        u_out[i] = clamped;
        alloc->u_prev[i] = clamped;
    }
}
