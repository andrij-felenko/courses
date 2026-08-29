#include "sensor_align.h"

/* Точні косинуси й синуси чвертей оберту: жодного sinf(), жодної похибки округлення. */
static const float CQ[4] = { 1.0f, 0.0f, -1.0f,  0.0f };
static const float SQ[4] = { 0.0f, 1.0f,  0.0f, -1.0f };

static int wrap4(int q) {
    q %= 4;
    if (q < 0) q += 4;
    return q;
}

mat3_t board_rotation_matrix(board_rotation_t r) {
    int i = wrap4(r.roll_q), j = wrap4(r.pitch_q), k = wrap4(r.yaw_q);
    mat3_t rx = { { { 1.0f, 0.0f,   0.0f   },
                    { 0.0f, CQ[i], -SQ[i]  },
                    { 0.0f, SQ[i],  CQ[i]  } } };
    mat3_t ry = { { {  CQ[j], 0.0f, SQ[j] },
                    {  0.0f,  1.0f, 0.0f  },
                    { -SQ[j], 0.0f, CQ[j] } } };
    mat3_t rz = { { { CQ[k], -SQ[k], 0.0f },
                    { SQ[k],  CQ[k], 0.0f },
                    { 0.0f,   0.0f,  1.0f } } };
    return mat3_mul(mat3_mul(rz, ry), rx);
}

static bool mat3_close(mat3_t a, mat3_t b) {
    for (int i = 0; i < 3; ++i)
        for (int j = 0; j < 3; ++j)
            if (fabsf(a.m[i][j] - b.m[i][j]) > 1.0e-3f) return false;
    return true;
}

int board_rotation_enumerate(mat3_t *out, int max_out) {
    if (!out || max_out <= 0) return 0;
    int n = 0;
    for (int r = 0; r < 4; ++r) {
        for (int p = 0; p < 4; ++p) {
            for (int y = 0; y < 4; ++y) {
                board_rotation_t rot;
                rot.roll_q = (signed char)r;
                rot.pitch_q = (signed char)p;
                rot.yaw_q = (signed char)y;
                mat3_t m = board_rotation_matrix(rot);
                bool seen = false;
                for (int i = 0; i < n && !seen; ++i) seen = mat3_close(m, out[i]);
                if (!seen) {
                    if (n >= max_out) return n;
                    out[n++] = m;
                }
            }
        }
    }
    return n;
}

static void rebuild(sensor_calib_t *c) {
    c->combined = mat3_mul(mat3_mul(c->r_board, c->r_align), c->scale_ortho);
}

void sensor_calib_identity(sensor_calib_t *c) {
    if (!c) return;
    for (int i = 0; i < 4; ++i) c->bias_c[i] = vec3_zero();
    c->t_ref_c = 25.0f;
    c->scale_ortho = mat3_identity();
    c->r_align = mat3_identity();
    c->r_board = mat3_identity();
    rebuild(c);
}

void sensor_calib_set_scale(sensor_calib_t *c, mat3_t s_ortho) {
    if (!c) return;
    c->scale_ortho = s_ortho;
    rebuild(c);
}

bool sensor_calib_set_misalignment(sensor_calib_t *c, vec3_t small_angles_rad) {
    if (!c || !vec3_is_finite(small_angles_rad)) return false;
    const float limit = 0.175f;   /* ~10°: далі малокутове наближення бреше помітно */
    if (fabsf(small_angles_rad.x) > limit ||
        fabsf(small_angles_rad.y) > limit ||
        fabsf(small_angles_rad.z) > limit) return false;

    float dphi = small_angles_rad.x, dtheta = small_angles_rad.y, dpsi = small_angles_rad.z;
    mat3_t approx = { { {  1.0f,   dpsi,  -dtheta },
                        { -dpsi,   1.0f,   dphi   },
                        {  dtheta, -dphi,  1.0f   } } };
    /* Наближення не ортогональне точно — Грам-Шмідт повертає його на многовид поворотів. */
    mat3_t clean;
    if (!mat3_orthonormalize(approx, &clean)) return false;
    c->r_align = clean;
    rebuild(c);
    return true;
}

void sensor_calib_set_board(sensor_calib_t *c, board_rotation_t rot) {
    if (!c) return;
    c->r_board = board_rotation_matrix(rot);
    rebuild(c);
}

void sensor_calib_set_bias_poly(sensor_calib_t *c, const vec3_t coeff[4], float t_ref_c) {
    if (!c || !coeff) return;
    for (int i = 0; i < 4; ++i) c->bias_c[i] = coeff[i];
    c->t_ref_c = t_ref_c;
}

vec3_t sensor_bias_at(const sensor_calib_t *c, float temp_c) {
    if (!c) return vec3_zero();
    if (!isfinite(temp_c)) temp_c = c->t_ref_c;
    /* Поза калібрувальною смугою куб полінома вибухає — тому затискаємо аргумент. */
    if (temp_c < -40.0f) temp_c = -40.0f;
    if (temp_c >  85.0f) temp_c =  85.0f;
    float d = temp_c - c->t_ref_c;
    /* Схема Горнера: b0 + d·(b1 + d·(b2 + d·b3)). */
    vec3_t b = c->bias_c[3];
    for (int i = 2; i >= 0; --i) b = vec3_add(c->bias_c[i], vec3_scale(b, d));
    return b;
}

vec3_t sensor_align_measurement(const sensor_calib_t *c, vec3_t raw, float temp_c) {
    if (!c || !vec3_is_finite(raw)) return vec3_zero();
    vec3_t unbiased = vec3_sub(raw, sensor_bias_at(c, temp_c));
    return mat3_mul_vec3(c->combined, unbiased);
}

bool sensor_calib_check(const sensor_calib_t *c, float *worst_ortho_err) {
    if (!c) return false;
    float e1 = mat3_orthogonality_error(c->r_align);
    float e2 = mat3_orthogonality_error(c->r_board);
    float worst = (e1 > e2) ? e1 : e2;
    if (worst_ortho_err) *worst_ortho_err = worst;
    /* Дзеркальна матриця (det < 0) перевернула б знак однієї осі — це не поворот. */
    if (mat3_det(c->r_align) < 0.5f || mat3_det(c->r_board) < 0.5f) return false;
    return worst < 1.0e-3f;
}
