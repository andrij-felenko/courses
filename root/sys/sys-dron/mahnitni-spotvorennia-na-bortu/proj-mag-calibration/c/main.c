#include <stdbool.h>
#include <stdint.h>
#include <string.h>
#include <math.h>

#define MAG_CAL_SECTORS_AZIMUTH   12
#define MAG_CAL_SECTORS_ELEVATION 6
#define MAG_CAL_TOTAL_BINS        (MAG_CAL_SECTORS_AZIMUTH * MAG_CAL_SECTORS_ELEVATION)
#define MAG_CAL_MIN_SAMPLES       36
#define MAG_CAL_MAX_PER_BIN       5

typedef struct {
    float hth[9][9];                       /* Матриця нормальних рівнянь Hᵀ·H */
    float ht1[9];                          /* Правий вектор Hᵀ·1 */
    uint8_t bin_counts[MAG_CAL_TOTAL_BINS];/* Лічильник відліків по секторах */
    uint32_t total_samples;                /* Загальна кількість врахованих точок */
    bool is_calibrated;                    /* Прапорець успішності обчислення */
    float v_hard[3];                       /* Вектор зміщення твердого заліза */
    float t_soft[3][3];                    /* Матриця компенсації м'якого заліза */
    float earth_field_uT;                  /* Очікувана напруженість поля Землі */
} mag_calibrator_t;

void mag_cal_init(mag_calibrator_t *cal, float earth_field_uT) {
    memset(cal, 0, sizeof(mag_calibrator_t));
    cal->earth_field_uT = (earth_field_uT > 10.0f) ? earth_field_uT : 45.0f;
    cal->t_soft[0][0] = 1.0f;
    cal->t_soft[1][1] = 1.0f;
    cal->t_soft[2][2] = 1.0f;
}

/* Визначення індексу просторового сектора за координатами вимірювання */
static int mag_cal_get_bin_index(float x, float y, float z) {
    float norm = sqrtf(x * x + y * y + z * z);
    if (norm < 1e-4f) return 0;

    float azimuth = atan2f(y, x); /* Діапазон [-π, +π] */
    if (azimuth < 0.0f) azimuth += 2.0f * (float)M_PI;
    int az_bin = (int)(azimuth / (2.0f * (float)M_PI / MAG_CAL_SECTORS_AZIMUTH));
    if (az_bin >= MAG_CAL_SECTORS_AZIMUTH) az_bin = MAG_CAL_SECTORS_AZIMUTH - 1;

    float elevation = asinf(z / norm); /* Діапазон [-π/2, +π/2] */
    float norm_elev = elevation + (float)M_PI * 0.5f; /* Діапазон [0, π] */
    int el_bin = (int)(norm_elev / ((float)M_PI / MAG_CAL_SECTORS_ELEVATION));
    if (el_bin >= MAG_CAL_SECTORS_ELEVATION) el_bin = MAG_CAL_SECTORS_ELEVATION - 1;

    return el_bin * MAG_CAL_SECTORS_AZIMUTH + az_bin;
}

/* Додавання сирого вимірювання до накопичувача МНК з фільтрацією надлишкових точок */
bool mag_cal_add_sample(mag_calibrator_t *cal, float x, float y, float z) {
    int bin = mag_cal_get_bin_index(x, y, z);
    if (cal->bin_counts[bin] >= MAG_CAL_MAX_PER_BIN) {
        return false; /* Сектор заповнений, пропускаємо дубль */
    }

    cal->bin_counts[bin]++;
    cal->total_samples++;

    /* Вектор базисних функцій квадрики H_i */
    float h[9];
    h[0] = x * x;
    h[1] = y * y;
    h[2] = z * z;
    h[3] = x * y;
    h[4] = x * z;
    h[5] = y * z;
    h[6] = x;
    h[7] = y;
    h[8] = z;

    /* Акумуляція симетричної матриці Hᵀ · H та вектора Hᵀ · 1 */
    for (int i = 0; i < 9; i++) {
        cal->ht1[i] += h[i];
        for (int j = 0; j < 9; j++) {
            cal->hth[i][j] += h[i] * h[j];
        }
    }
    return true;
}

/* Розв'язання лінійної системи 9×9 методом Гаусса з вибором головного елемента */
static bool solve_linear_system_9x9(float A[9][9], float b[9], float x_out[9]) {
    float M[9][10];
    for (int i = 0; i < 9; i++) {
        for (int j = 0; j < 9; j++) {
            M[i][j] = A[i][j];
        }
        M[i][9] = b[i];
    }

    /* Прямий хід з вибором головного елемента по стовпцю */
    for (int col = 0; col < 9; col++) {
        int max_row = col;
        float max_val = fabsf(M[col][col]);
        for (int row = col + 1; row < 9; row++) {
            float v = fabsf(M[row][col]);
            if (v > max_val) {
                max_val = v;
                max_row = row;
            }
        }
        if (max_val < 1e-9f) return false; /* Матриця сингулярна або погано обумовлена */

        if (max_row != col) {
            for (int k = col; k < 10; k++) {
                float tmp = M[col][k];
                M[col][k] = M[max_row][k];
                M[max_row][k] = tmp;
            }
        }

        for (int row = col + 1; row < 9; row++) {
            float factor = M[row][col] / M[col][col];
            for (int k = col; k < 10; k++) {
                M[row][k] -= factor * M[col][k];
            }
        }
    }

    /* Зворотний хід Гаусса */
    for (int row = 8; row >= 0; row--) {
        float sum = M[row][9];
        for (int col = row + 1; col < 9; col++) {
            sum -= M[row][col] * x_out[col];
        }
        x_out[row] = sum / M[row][row];
    }
    return true;
}

/* Аналітичне обернення матриці 3×3 через алгебраїчні доповнення */
static bool invert_matrix_3x3(const float A[3][3], float inv[3][3]) {
    float det = A[0][0] * (A[1][1] * A[2][2] - A[1][2] * A[2][1]) -
                A[0][1] * (A[1][0] * A[2][2] - A[1][2] * A[2][0]) +
                A[0][2] * (A[1][0] * A[2][1] - A[1][2] * A[2][0]);
    if (fabsf(det) < 1e-12f) return false;

    float inv_det = 1.0f / det;
    inv[0][0] = (A[1][1] * A[2][2] - A[1][2] * A[2][1]) * inv_det;
    inv[0][1] = (A[0][2] * A[2][1] - A[0][1] * A[2][2]) * inv_det;
    inv[0][2] = (A[0][1] * A[1][2] - A[0][2] * A[1][1]) * inv_det;
    inv[1][0] = (A[1][2] * A[2][0] - A[1][0] * A[2][2]) * inv_det;
    inv[1][1] = (A[0][0] * A[2][2] - A[0][2] * A[2][0]) * inv_det;
    inv[1][2] = (A[0][2] * A[1][0] - A[0][0] * A[1][2]) * inv_det;
    inv[2][0] = (A[1][0] * A[2][1] - A[1][1] * A[2][0]) * inv_det;
    inv[2][1] = (A[0][1] * A[2][0] - A[0][0] * A[2][1]) * inv_det;
    inv[2][2] = (A[0][0] * A[1][1] - A[0][1] * A[1][0]) * inv_det;
    return true;
}

/* Обчислення підсумкових параметрів твердого та м'якого заліза */
bool mag_cal_compute(mag_calibrator_t *cal) {
    if (cal->total_samples < MAG_CAL_MIN_SAMPLES) return false;

    float p[9];
    if (!solve_linear_system_9x9(cal->hth, cal->ht1, p)) return false;

    /* Відновлення матриці форми A та вектора лінійних коефіцієнтів b */
    float A[3][3] = {
        { p[0],        p[3] * 0.5f, p[4] * 0.5f },
        { p[3] * 0.5f, p[1],        p[5] * 0.5f },
        { p[4] * 0.5f, p[5] * 0.5f, p[2]        }
    };
    float b[3] = { p[6] * 0.5f, p[7] * 0.5f, p[8] * 0.5f };

    float A_inv[3][3];
    if (!invert_matrix_3x3(A, A_inv)) return false;

    /* Центр еліпсоїда V_hard = -A⁻¹ · b */
    for (int i = 0; i < 3; i++) {
        cal->v_hard[i] = -(A_inv[i][0] * b[0] + A_inv[i][1] * b[1] + A_inv[i][2] * b[2]);
    }

    /* Масштаб форми scale = V_hardᵀ · A · V_hard + 1.0 */
    float Av[3] = {
        A[0][0] * cal->v_hard[0] + A[0][1] * cal->v_hard[1] + A[0][2] * cal->v_hard[2],
        A[1][0] * cal->v_hard[0] + A[1][1] * cal->v_hard[1] + A[1][2] * cal->v_hard[2],
        A[2][0] * cal->v_hard[0] + A[2][1] * cal->v_hard[1] + A[2][2] * cal->v_hard[2]
    };
    float scale = cal->v_hard[0] * Av[0] + cal->v_hard[1] * Av[1] + cal->v_hard[2] * Av[2] + 1.0f;
    if (scale <= 1e-6f) return false;

    /* Нормована матриця форми M = A / scale */
    float M[3][3];
    for (int i = 0; i < 3; i++) {
        for (int j = 0; j < 3; j++) {
            M[i][j] = A[i][j] / scale;
        }
    }

    /* Розклад Холецького M = L · Lᵀ */
    float L[3][3] = {0};
    if (M[0][0] <= 0.0f) return false;
    L[0][0] = sqrtf(M[0][0]);
    L[1][0] = M[1][0] / L[0][0];
    L[2][0] = M[2][0] / L[0][0];

    float d11 = M[1][1] - L[1][0] * L[1][0];
    if (d11 <= 0.0f) return false;
    L[1][1] = sqrtf(d11);
    L[2][1] = (M[2][1] - L[2][0] * L[1][0]) / L[1][1];

    float d22 = M[2][2] - L[2][0] * L[2][0] - L[2][1] * L[2][1];
    if (d22 <= 0.0f) return false;
    L[2][2] = sqrtf(d22);

    /* Матриця компенсації T = B₀ · Lᵀ (верхня трикутна) */
    for (int i = 0; i < 3; i++) {
        for (int j = 0; j < 3; j++) {
            cal->t_soft[i][j] = cal->earth_field_uT * L[j][i];
        }
    }

    cal->is_calibrated = true;
    return true;
}

/* Онлайн-корекція сирих відліків у циклі керування */
void mag_cal_apply(const mag_calibrator_t *cal, float rx, float ry, float rz,
                   float *cx, float *cy, float *cz) {
    if (!cal->is_calibrated) {
        *cx = rx; *cy = ry; *cz = rz;
        return;
    }
    float dx = rx - cal->v_hard[0];
    float dy = ry - cal->v_hard[1];
    float dz = rz - cal->v_hard[2];

    *cx = cal->t_soft[0][0] * dx + cal->t_soft[0][1] * dy + cal->t_soft[0][2] * dz;
    *cy = cal->t_soft[1][0] * dx + cal->t_soft[1][1] * dy + cal->t_soft[1][2] * dz;
    *cz = cal->t_soft[2][0] * dx + cal->t_soft[2][1] * dy + cal->t_soft[2][2] * dz;
}
