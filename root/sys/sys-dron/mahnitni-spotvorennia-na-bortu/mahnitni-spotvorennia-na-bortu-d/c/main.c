#include <stdbool.h>
#include <stdint.h>
#include <string.h>
#include <math.h>

#define MAG_BINS_AZIMUTH   12
#define MAG_BINS_ELEVATION 6
#define MAG_TOTAL_BINS     (MAG_BINS_AZIMUTH * MAG_BINS_ELEVATION)
#define MAG_MIN_SAMPLES    36
#define MAG_MAX_PER_BIN    5

typedef struct {
    float hth[9][9];                   /* Матриця накопичення нормальних рівнянь Hᵀ·H */
    float ht1[9];                      /* Вектор накопичення Hᵀ·1 */
    uint8_t bin_counts[MAG_TOTAL_BINS];/* Лічильники точок по секторах сфери */
    uint32_t total_samples;            /* Кількість прийнятих точок */
    bool is_calibrated;                /* Прапорець готовності калібрування */
    float v_hard[3];                   /* Оцінений вектор твердого заліза */
    float t_soft[3][3];                /* Матриця корекції м'якого заліза T = W_soft⁻¹ */
    float field_radius_uT;             /* Еталонна напруженість поля Землі B₀ */
} mag_cal_t;

void mag_cal_init(mag_cal_t *cal, float earth_field_uT) {
    memset(cal, 0, sizeof(mag_cal_t));
    cal->field_radius_uT = (earth_field_uT > 10.0f) ? earth_field_uT : 45.0f;
    cal->t_soft[0][0] = 1.0f;
    cal->t_soft[1][1] = 1.0f;
    cal->t_soft[2][2] = 1.0f;
}

/* Визначення індексу сектора на сфері */
static int mag_cal_bin_index(float x, float y, float z) {
    float norm = sqrtf(x * x + y * y + z * z);
    if (norm < 1e-4f) return 0;

    float az = atan2f(y, x);
    if (az < 0.0f) az += 2.0f * (float)M_PI;
    int az_bin = (int)(az / (2.0f * (float)M_PI / MAG_BINS_AZIMUTH));
    if (az_bin >= MAG_BINS_AZIMUTH) az_bin = MAG_BINS_AZIMUTH - 1;

    float el = asinf(z / norm) + (float)M_PI * 0.5f;
    int el_bin = (int)(el / ((float)M_PI / MAG_BINS_ELEVATION));
    if (el_bin >= MAG_BINS_ELEVATION) el_bin = MAG_BINS_ELEVATION - 1;

    return el_bin * MAG_BINS_AZIMUTH + az_bin;
}

/* Додавання відліку до накопичувача */
bool mag_cal_collect(mag_cal_t *cal, float x, float y, float z) {
    int bin = mag_cal_bin_index(x, y, z);
    if (cal->bin_counts[bin] >= MAG_MAX_PER_BIN) return false;

    cal->bin_counts[bin]++;
    cal->total_samples++;

    float h[9] = { x*x, y*y, z*z, x*y, x*z, y*z, x, y, z };
    for (int i = 0; i < 9; i++) {
        cal->ht1[i] += h[i];
        for (int j = 0; j < 9; j++) {
            cal->hth[i][j] += h[i] * h[j];
        }
    }
    return true;
}

/* Розв'язання лінійної системи 9×9 методом Гаусса з вибором головного елемента */
static bool solve_gauss_9x9(float A[9][9], float b[9], float x_out[9]) {
    float M[9][10];
    for (int i = 0; i < 9; i++) {
        for (int j = 0; j < 9; j++) M[i][j] = A[i][j];
        M[i][9] = b[i];
    }
    for (int col = 0; col < 9; col++) {
        int pivot = col;
        float max_val = fabsf(M[col][col]);
        for (int row = col + 1; row < 9; row++) {
            if (fabsf(M[row][col]) > max_val) {
                max_val = fabsf(M[row][col]);
                pivot = row;
            }
        }
        if (max_val < 1e-9f) return false;
        if (pivot != col) {
            for (int k = col; k < 10; k++) {
                float tmp = M[col][k];
                M[col][k] = M[pivot][k];
                M[pivot][k] = tmp;
            }
        }
        for (int row = col + 1; row < 9; row++) {
            float factor = M[row][col] / M[col][col];
            for (int k = col; k < 10; k++) M[row][k] -= factor * M[col][k];
        }
    }
    for (int row = 8; row >= 0; row--) {
        float sum = M[row][9];
        for (int col = row + 1; col < 9; col++) sum -= M[row][col] * x_out[col];
        x_out[row] = sum / M[row][row];
    }
    return true;
}

/* Фінальний розрахунок матриці T та вектора V_hard */
bool mag_cal_finalize(mag_cal_t *cal) {
    if (cal->total_samples < MAG_MIN_SAMPLES) return false;

    float p[9];
    if (!solve_gauss_9x9(cal->hth, cal->ht1, p)) return false;

    float A[3][3] = {
        { p[0],        p[3] * 0.5f, p[4] * 0.5f },
        { p[3] * 0.5f, p[1],        p[5] * 0.5f },
        { p[4] * 0.5f, p[5] * 0.5f, p[2]        }
    };
    float b[3] = { p[6] * 0.5f, p[7] * 0.5f, p[8] * 0.5f };

    /* Обернення матриці A */
    float det = A[0][0]*(A[1][1]*A[2][2] - A[1][2]*A[2][1]) -
                A[0][1]*(A[1][0]*A[2][2] - A[1][2]*A[2][0]) +
                A[0][2]*(A[1][0]*A[2][1] - A[1][1]*A[2][0]);
    if (fabsf(det) < 1e-12f) return false;

    float inv_det = 1.0f / det;
    float A_inv[3][3] = {
        { (A[1][1]*A[2][2] - A[1][2]*A[2][1])*inv_det, (A[0][2]*A[2][1] - A[0][1]*A[2][2])*inv_det, (A[0][1]*A[1][2] - A[0][2]*A[1][1])*inv_det },
        { (A[1][2]*A[2][0] - A[1][0]*A[2][2])*inv_det, (A[0][0]*A[2][2] - A[0][2]*A[2][0])*inv_det, (A[0][2]*A[1][0] - A[0][0]*A[1][2])*inv_det },
        { (A[1][0]*A[2][1] - A[1][1]*A[2][0])*inv_det, (A[0][1]*A[2][0] - A[0][0]*A[2][1])*inv_det, (A[0][0]*A[1][1] - A[0][1]*A[1][0])*inv_det }
    };

    /* V_hard = -A⁻¹ · b */
    for (int i = 0; i < 3; i++) {
        cal->v_hard[i] = -(A_inv[i][0]*b[0] + A_inv[i][1]*b[1] + A_inv[i][2]*b[2]);
    }

    float Av[3] = {
        A[0][0]*cal->v_hard[0] + A[0][1]*cal->v_hard[1] + A[0][2]*cal->v_hard[2],
        A[1][0]*cal->v_hard[0] + A[1][1]*cal->v_hard[1] + A[1][2]*cal->v_hard[2],
        A[2][0]*cal->v_hard[0] + A[2][1]*cal->v_hard[1] + A[2][2]*cal->v_hard[2]
    };
    float scale = cal->v_hard[0]*Av[0] + cal->v_hard[1]*Av[1] + cal->v_hard[2]*Av[2] + 1.0f;
    if (scale <= 1e-6f) return false;

    /* Розклад Холецького матриці M = A / scale */
    float M[3][3];
    for (int i = 0; i < 3; i++) {
        for (int j = 0; j < 3; j++) M[i][j] = A[i][j] / scale;
    }

    if (M[0][0] <= 0.0f) return false;
    float L00 = sqrtf(M[0][0]);
    float L10 = M[1][0] / L00;
    float L20 = M[2][0] / L00;

    float d11 = M[1][1] - L10 * L10;
    if (d11 <= 0.0f) return false;
    float L11 = sqrtf(d11);
    float L21 = (M[2][1] - L20 * L10) / L11;

    float d22 = M[2][2] - L20 * L20 - L21 * L21;
    if (d22 <= 0.0f) return false;
    float L22 = sqrtf(d22);

    /* T = B₀ · Lᵀ */
    cal->t_soft[0][0] = cal->field_radius_uT * L00;
    cal->t_soft[0][1] = cal->field_radius_uT * L10;
    cal->t_soft[0][2] = cal->field_radius_uT * L20;

    cal->t_soft[1][0] = 0.0f;
    cal->t_soft[1][1] = cal->field_radius_uT * L11;
    cal->t_soft[1][2] = cal->field_radius_uT * L21;

    cal->t_soft[2][0] = 0.0f;
    cal->t_soft[2][1] = 0.0f;
    cal->t_soft[2][2] = cal->field_radius_uT * L22;

    cal->is_calibrated = true;
    return true;
}

/* Корекція відліку в польотному циклі */
void mag_cal_correct(const mag_cal_t *cal, float rx, float ry, float rz,
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
