#include <stdint.h>
#include <stdbool.h>

#define CALIB_LUT_X_SIZE  5
#define CALIB_LUT_T_SIZE  4

typedef enum {
    CALIB_OK = 0,
    CALIB_ERR_NULL_PTR = -1,
    CALIB_WARN_CLAMPED_LOW = 1,
    CALIB_WARN_CLAMPED_HIGH = 2
} calib_status_t;

/* Структура конфігурації двовимірної таблиці калібрування (2D LUT) */
typedef struct {
    float x_grid[CALIB_LUT_X_SIZE];                     /* Вузли сирого сигналу ADC */
    float t_grid[CALIB_LUT_T_SIZE];                     /* Вузли температури (°C)   */
    float lut_values[CALIB_LUT_T_SIZE][CALIB_LUT_X_SIZE]; /* Калібровані значення фізичної величини */
} calib_lut2d_config_t;

/* Структура коефіцієнтів полінома 2-го порядку P(U, T) */
typedef struct {
    float c00, c10, c01;
    float c11;
    float c20, c02;
    float c21, c12;
    float c22;
} calib_poly2d_config_t;

/* Білінійна інтерполяція за 2D LUT з безпечним обмеженням меж (clamping) */
calib_status_t sensor_compensate_lut2d(const calib_lut2d_config_t *cfg,
                                       float raw_x, float raw_t,
                                       float *out_val) {
    if (!cfg || !out_val) {
        return CALIB_ERR_NULL_PTR;
    }

    calib_status_t status = CALIB_OK;

    /* Обмеження сигналу X у межах сітки калібрування */
    float x = raw_x;
    if (x <= cfg->x_grid[0]) {
        x = cfg->x_grid[0];
        status = CALIB_WARN_CLAMPED_LOW;
    } else if (x >= cfg->x_grid[CALIB_LUT_X_SIZE - 1]) {
        x = cfg->x_grid[CALIB_LUT_X_SIZE - 1];
        status = CALIB_WARN_CLAMPED_HIGH;
    }

    /* Обмеження температури T у межах сітки */
    float t = raw_t;
    if (t <= cfg->t_grid[0]) {
        t = cfg->t_grid[0];
        status = CALIB_WARN_CLAMPED_LOW;
    } else if (t >= cfg->t_grid[CALIB_LUT_T_SIZE - 1]) {
        t = cfg->t_grid[CALIB_LUT_T_SIZE - 1];
        status = CALIB_WARN_CLAMPED_HIGH;
    }

    /* Пошук індексів комірки сітки для X */
    int i = 0;
    for (int k = 0; k < CALIB_LUT_X_SIZE - 2; ++k) {
        if (x >= cfg->x_grid[k + 1]) {
            i = k + 1;
        }
    }

    /* Пошук індексів комірки сітки для T */
    int j = 0;
    for (int k = 0; k < CALIB_LUT_T_SIZE - 2; ++k) {
        if (t >= cfg->t_grid[k + 1]) {
            j = k + 1;
        }
    }

    /* Локальні нормалізовані координати всередині комірки [0.0 ... 1.0] */
    const float dx = cfg->x_grid[i + 1] - cfg->x_grid[i];
    const float dt = cfg->t_grid[j + 1] - cfg->t_grid[j];
    const float u = (dx > 1e-7f) ? ((x - cfg->x_grid[i]) / dx) : 0.0f;
    const float v = (dt > 1e-7f) ? ((t - cfg->t_grid[j]) / dt) : 0.0f;

    /* Чотири кутові вузли */
    const float q11 = cfg->lut_values[j][i];
    const float q21 = cfg->lut_values[j][i + 1];
    const float q12 = cfg->lut_values[j + 1][i];
    const float q22 = cfg->lut_values[j + 1][i + 1];

    /* Білінійна інтерполяція */
    const float r1 = q11 + u * (q21 - q11);
    const float r2 = q12 + u * (q22 - q12);
    *out_val = r1 + v * (r2 - r1);

    return status;
}

/* Обчислення полінома 2-го порядку за схемою Горнера */
calib_status_t sensor_compensate_poly2d(const calib_poly2d_config_t *cfg,
                                        float raw_u, float raw_t,
                                        float *out_val) {
    if (!cfg || !out_val) {
        return CALIB_ERR_NULL_PTR;
    }

    const float u = raw_u;
    const float t = raw_t;

    const float term_const = cfg->c00 + t * (cfg->c01 + t * cfg->c02);
    const float term_u1    = cfg->c10 + t * (cfg->c11 + t * cfg->c12);
    const float term_u2    = cfg->c20 + t * (cfg->c21 + t * cfg->c22);

    *out_val = term_const + u * (term_u1 + u * term_u2);

    return CALIB_OK;
}
