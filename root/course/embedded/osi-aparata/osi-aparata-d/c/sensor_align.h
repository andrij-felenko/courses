#ifndef SENSOR_ALIGN_H
#define SENSOR_ALIGN_H

#include "linalg.h"

/* Дискретна орієнтація плати: чверті оберту навколо осей тіла, R = Rz·Ry·Rx.
   Трійка чвертей вичерпує всі 24 положення куба. */
typedef struct { signed char roll_q, pitch_q, yaw_q; } board_rotation_t;

#define BOARD_ROTATION_COUNT 24

mat3_t board_rotation_matrix(board_rotation_t r);
/* Складає в out усі унікальні матриці плати; повертає їхню кількість. */
int    board_rotation_enumerate(mat3_t *out, int max_out);

typedef struct {
    vec3_t bias_c[4];    /* b0..b3 — поліном зміщення нуля за температурою */
    float  t_ref_c;      /* базова температура калібрування, °C */
    mat3_t scale_ortho;  /* S: чутливість і неортогональність кремнію */
    mat3_t r_align;      /* дрібний монтажний перекіс паяння */
    mat3_t r_board;      /* дискретна орієнтація плати в рамі */
    mat3_t combined;     /* R_board·R_align·S — рахуємо раз, у циклі одне множення */
} sensor_calib_t;

void   sensor_calib_identity(sensor_calib_t *c);
void   sensor_calib_set_scale(sensor_calib_t *c, mat3_t s_ortho);
/* Малокутова модель перекосу; хибно, якщо кути завеликі для неї. */
bool   sensor_calib_set_misalignment(sensor_calib_t *c, vec3_t small_angles_rad);
void   sensor_calib_set_board(sensor_calib_t *c, board_rotation_t rot);
void   sensor_calib_set_bias_poly(sensor_calib_t *c, const vec3_t coeff[4], float t_ref_c);

vec3_t sensor_bias_at(const sensor_calib_t *c, float temp_c);
/* Повний конвеєр: v_body = R_board·R_align·S·(v_raw − b_bias(T)). */
vec3_t sensor_align_measurement(const sensor_calib_t *c, vec3_t raw, float temp_c);
/* Обидві матриці поворотів мають лишатися ортогональними — інакше калібрування зіпсоване. */
bool   sensor_calib_check(const sensor_calib_t *c, float *worst_ortho_err);

#endif /* SENSOR_ALIGN_H */
