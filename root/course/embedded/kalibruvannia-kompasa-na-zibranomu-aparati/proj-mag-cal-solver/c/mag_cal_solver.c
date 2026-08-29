/* ==========================================================================
 *  mag_cal_solver.c — Левенберг — Марквардт на 9 параметрів
 *
 *  p = [ V0x, V0y, V0z, W11, W12, W13, W22, W23, W33 ]
 *  r_i = ‖ W · (B_i − V0) ‖ − B_earth        (нев'язка одного виміру, мкТл)
 *
 *  Матриця W тримається симетричною за побудовою: несиметрична частина —
 *  це поворот, а поворот сенсора вже враховано монтажною матрицею плати.
 * ========================================================================== */

#include <string.h>

#include "mag_cal_linalg.h"
#include "mag_cal_solver.h"

/* Порожній крок демпфування: скільки разів на одній ітерації дозволено
 * підняти λ, перш ніж визнати, що далі не рухаємось. */
#define MAG_CAL_MAX_DAMPING_TRIES 8
#define MAG_CAL_LAMBDA_MAX        1.0e9f
#define MAG_CAL_LAMBDA_MIN        1.0e-9f

const char *mag_cal_solve_status_str(mag_cal_solve_status_t st) {
    switch (st) {
        case MAG_CAL_SOLVE_OK:              return "ok";
        case MAG_CAL_SOLVE_LOW_COVERAGE:    return "мале покриття сфери";
        case MAG_CAL_SOLVE_FEW_POINTS:      return "замало точок";
        case MAG_CAL_SOLVE_SINGULAR:        return "вироджені нормальні рівняння";
        case MAG_CAL_SOLVE_DIVERGED:        return "розбіжність параметрів";
        case MAG_CAL_SOLVE_NO_CONVERGE:     return "не збігся за ліміт ітерацій";
        case MAG_CAL_SOLVE_POOR_FITNESS:    return "завелика нев'язка RMS";
        case MAG_CAL_SOLVE_ILL_CONDITIONED: return "погана зумовленість W";
        default:                            return "невідомий стан";
    }
}

static mat3_t params_to_matrix(const float p[9]) {
    return (mat3_t){{
        { p[3], p[4], p[5] },
        { p[4], p[6], p[7] },
        { p[5], p[7], p[8] }
    }};
}

static vec3_t params_to_offset(const float p[9]) {
    return (vec3_t){ p[0], p[1], p[2] };
}

/* Сума квадратів нев'язок для заданого вектора параметрів */
static float mag_cal_cost(const mag_cal_collector_t *col, const float p[9],
                          float earth_b) {
    const mat3_t W  = params_to_matrix(p);
    const vec3_t V0 = params_to_offset(p);

    float sum_sq = 0.0f;
    for (int b = 0; b < MAG_CAL_TOTAL_BINS; b++) {
        for (int s = 0; s < col->sample_count[b]; s++) {
            const vec3_t d   = vec3_sub(col->samples[b][s], V0);
            const float  mod = vec3_norm(mat3_mul_vec(&W, d));
            const float  r   = mod - earth_b;
            sum_sq += r * r;
        }
    }
    return sum_sq;
}

/* Накопичення H = JᵀJ і g = Jᵀr за один прохід по хмарі.
 * Другу похідну не рахуємо: для задачі найменших квадратів наближення
 * Гаусса — Ньютона стійкіше, ніж повний гессіан із шумними даними. */
static float mag_cal_normal_equations(const mag_cal_collector_t *col,
                                      const float p[9], float earth_b,
                                      float H[9][9], float g[9]) {
    memset(H, 0, sizeof(float) * 9 * 9);
    memset(g, 0, sizeof(float) * 9);

    const mat3_t W  = params_to_matrix(p);
    const vec3_t V0 = params_to_offset(p);

    float sum_sq = 0.0f;

    for (int b = 0; b < MAG_CAL_TOTAL_BINS; b++) {
        for (int s = 0; s < col->sample_count[b]; s++) {
            const vec3_t d   = vec3_sub(col->samples[b][s], V0);
            const vec3_t cal = mat3_mul_vec(&W, d);

            float cal_norm = vec3_norm(cal);
            if (cal_norm < 1e-4f) cal_norm = 1e-4f;   /* точка сіла в центр */

            const float r = cal_norm - earth_b;
            sum_sq += r * r;

            /* u = ∂‖cal‖/∂cal — одиничний вектор уздовж скоригованого поля */
            const vec3_t u = vec3_scale(cal, 1.0f / cal_norm);

            float J[9];
            /* Похідні по зміщенню: ∂r/∂V0 = −Wᵀu, і W симетрична */
            J[0] = -(u.x * W.m[0][0] + u.y * W.m[1][0] + u.z * W.m[2][0]);
            J[1] = -(u.x * W.m[0][1] + u.y * W.m[1][1] + u.z * W.m[2][1]);
            J[2] = -(u.x * W.m[0][2] + u.y * W.m[1][2] + u.z * W.m[2][2]);

            /* Похідні по елементах W; позадіагональні входять двічі, бо
             * параметр W12 сидить одночасно в комірках (0,1) і (1,0). */
            J[3] = u.x * d.x;                       /* W11 */
            J[4] = u.x * d.y + u.y * d.x;           /* W12 */
            J[5] = u.x * d.z + u.z * d.x;           /* W13 */
            J[6] = u.y * d.y;                       /* W22 */
            J[7] = u.y * d.z + u.z * d.y;           /* W23 */
            J[8] = u.z * d.z;                       /* W33 */

            for (int j = 0; j < 9; j++) {
                g[j] += J[j] * r;
                for (int k = j; k < 9; k++) {        /* симетрія: пів матриці */
                    H[j][k] += J[j] * J[k];
                }
            }
        }
    }

    for (int j = 1; j < 9; j++) {
        for (int k = 0; k < j; k++) {
            H[j][k] = H[k][j];
        }
    }
    return sum_sq;
}

/* Параметри не мають права тікати в нефізичну область: зміщення більше
 * за півтори тисячі мкТл або підсилення більше за п'ятірку означають, що
 * хмара вироджена, а не що на апараті стільки заліза. */
static bool mag_cal_params_sane(const float p[9]) {
    for (int i = 0; i < 9; i++) {
        if (!isfinite(p[i])) return false;
    }
    if (fabsf(p[0]) > MAG_CAL_MAX_OFFSET_UT ||
        fabsf(p[1]) > MAG_CAL_MAX_OFFSET_UT ||
        fabsf(p[2]) > MAG_CAL_MAX_OFFSET_UT) {
        return false;
    }
    for (int i = 3; i < 9; i++) {
        if (fabsf(p[i]) > MAG_CAL_MAX_GAIN) return false;
    }
    return true;
}

mag_cal_solve_status_t mag_cal_run_solver(const mag_cal_collector_t *col,
                                          mag_cal_result_t *out) {
    memset(out, 0, sizeof(*out));
    out->coverage_pct = mag_cal_collector_coverage(col);
    out->earth_field  = col->target_earth_field;
    out->points_used  = col->total_points;

    if (out->coverage_pct < MAG_CAL_MIN_COVERAGE_PCT) {
        return MAG_CAL_SOLVE_LOW_COVERAGE;
    }
    if (col->total_points < MAG_CAL_MIN_POINTS) {
        return MAG_CAL_SOLVE_FEW_POINTS;
    }

    const float earth_b = col->target_earth_field;

    /* Початкове наближення: центр — вибіркове середнє хмари, W — одинична.
     * Просторове квотування робить це середнє чесною оцінкою центра сфери. */
    float p[9] = { 0.0f, 0.0f, 0.0f, 1.0f, 0.0f, 0.0f, 1.0f, 0.0f, 1.0f };
    {
        vec3_t sum = { 0.0f, 0.0f, 0.0f };
        for (int b = 0; b < MAG_CAL_TOTAL_BINS; b++) {
            for (int s = 0; s < col->sample_count[b]; s++) {
                sum = vec3_add(sum, col->samples[b][s]);
            }
        }
        const float inv_n = 1.0f / (float)col->total_points;
        p[0] = sum.x * inv_n;
        p[1] = sum.y * inv_n;
        p[2] = sum.z * inv_n;
    }

    float lambda    = 1.0e-3f;
    float cost      = mag_cal_cost(col, p, earth_b);
    bool  converged = false;
    bool  singular  = false;
    uint8_t accepted = 0;

    for (int iter = 0; iter < MAG_CAL_MAX_ITERATIONS && !converged; iter++) {
        float H[9][9];
        float g[9];
        cost = mag_cal_normal_equations(col, p, earth_b, H, g);

        bool step_taken = false;

        for (int attempt = 0; attempt < MAG_CAL_MAX_DAMPING_TRIES && !step_taken; attempt++) {
            /* Демпфування Марквардта: масштабуємо саме діагональ, тож крок
             * лишається інваріантним до одиниць окремих параметрів. */
            float A[9][9];
            memcpy(A, H, sizeof(A));
            for (int i = 0; i < 9; i++) {
                A[i][i] += lambda * (H[i][i] + 1e-3f);
            }

            float rhs[9];
            for (int i = 0; i < 9; i++) {
                rhs[i] = -g[i];
            }

            float dp[9];
            if (!mag_cal_solve9(A, rhs, dp)) {
                /* Головний елемент помер: піднімаємо λ вдесятеро — матриця
                 * стає діагонально домінантною, а метод — градієнтним спуском. */
                lambda *= 10.0f;
                if (lambda > MAG_CAL_LAMBDA_MAX) { singular = true; break; }
                continue;
            }

            float p_try[9];
            float step_sq = 0.0f;
            for (int i = 0; i < 9; i++) {
                p_try[i] = p[i] + dp[i];
                step_sq += dp[i] * dp[i];
            }

            if (!mag_cal_params_sane(p_try)) {
                lambda *= 10.0f;
                if (lambda > MAG_CAL_LAMBDA_MAX) { singular = true; break; }
                continue;
            }

            const float cost_try = mag_cal_cost(col, p_try, earth_b);

            if (cost_try < cost) {
                /* Крок покращив нев'язку — приймаємо його й слабшаємо λ,
                 * повертаючись до швидкого гаусс-ньютонівського режиму. */
                memcpy(p, p_try, sizeof(p));
                const float gain = (cost - cost_try) / (cost > 0.0f ? cost : 1.0f);
                cost = cost_try;
                lambda *= 0.2f;
                if (lambda < MAG_CAL_LAMBDA_MIN) lambda = MAG_CAL_LAMBDA_MIN;
                accepted++;
                step_taken = true;

                if (sqrtf(step_sq) < 1e-4f || gain < 1e-6f) {
                    converged = true;
                }
            } else {
                /* Крок завеликий — відкочуємо його й підтягуємо демпфування */
                lambda *= 10.0f;
                if (lambda > MAG_CAL_LAMBDA_MAX) { singular = true; break; }
            }
        }

        if (singular) break;
        if (!step_taken) {
            /* Жодне демпфування не дало покращення: далі рухатись нікуди */
            converged = true;
        }
    }

    out->offset     = params_to_offset(p);
    out->soft_iron  = params_to_matrix(p);
    out->iterations = accepted;

    /* Підсумкові метрики рахуємо ще раз явно — саме їх побачить оператор
     * і саме вони поїдуть у Flash, тож вони не мають бути побічним ефектом. */
    float  sum_sq     = 0.0f;
    float  sum_radius = 0.0f;
    for (int b = 0; b < MAG_CAL_TOTAL_BINS; b++) {
        for (int s = 0; s < col->sample_count[b]; s++) {
            const vec3_t cal = mat3_mul_vec(&out->soft_iron,
                                            vec3_sub(col->samples[b][s], out->offset));
            const float mod = vec3_norm(cal);
            const float err = mod - earth_b;
            sum_sq     += err * err;
            sum_radius += mod;
        }
    }
    const float inv_n = 1.0f / (float)col->total_points;
    out->rms_residual  = sqrtf(sum_sq * inv_n);
    out->sphere_radius = sum_radius * inv_n;
    out->condition_num = mat3_condition(&out->soft_iron);

    if (singular) {
        return MAG_CAL_SOLVE_SINGULAR;
    }
    if (!isfinite(out->rms_residual) || !mag_cal_params_sane(p)) {
        return MAG_CAL_SOLVE_DIVERGED;
    }
    if (!converged && accepted == 0) {
        return MAG_CAL_SOLVE_NO_CONVERGE;
    }
    if (out->rms_residual > MAG_CAL_MAX_RMS_UT) {
        return MAG_CAL_SOLVE_POOR_FITNESS;
    }
    if (out->condition_num >= MAG_CAL_MAX_CONDITION) {
        return MAG_CAL_SOLVE_ILL_CONDITIONED;
    }

    out->is_valid = true;
    return MAG_CAL_SOLVE_OK;
}

vec3_t mag_cal_apply(vec3_t raw, const mag_cal_result_t *cal) {
    if (!cal->is_valid) {
        return raw;
    }
    return mat3_mul_vec(&cal->soft_iron, vec3_sub(raw, cal->offset));
}
