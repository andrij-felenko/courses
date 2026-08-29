#include "calib6.h"

#include <string.h>

/* Параметри: p[0..5] — m00, m10, m11, m20, m21, m22; p[6..8] — зсув.
   Рахуємо в double: калібрування йде раз на стенді, а не в гарячому циклі,
   і нормальні рівняння з елементами порядку g⁴ у float погано обумовлені. */
#define NP 9

static const int ACTIVE_DIAG[6] = { 0, 2, 5, 6, 7, 8 };
static const int ACTIVE_FULL[9] = { 0, 1, 2, 3, 4, 5, 6, 7, 8 };

const char *calib6_status_text(calib6_status_t s) {
    switch (s) {
        case CALIB6_OK:                  return "ок";
        case CALIB6_ERR_ARGS:            return "некоректні аргументи або нескінченні виміри";
        case CALIB6_ERR_FEW_POSITIONS:   return "замало позицій для обраної моделі";
        case CALIB6_ERR_NOT_SPANNING:    return "позиції не покривають усі шість граней";
        case CALIB6_ERR_SINGULAR:        return "вироджені нормальні рівняння";
        case CALIB6_ERR_NO_CONVERGENCE:  return "ітерації не зійшлися";
        default:                         return "невідомий стан";
    }
}

static double residual(const double p[NP], vec3_t a, double g2, double jac[NP]) {
    double ux = (double)a.x - p[6];
    double uy = (double)a.y - p[7];
    double uz = (double)a.z - p[8];
    double y0 = p[0] * ux;
    double y1 = p[1] * ux + p[2] * uy;
    double y2 = p[3] * ux + p[4] * uy + p[5] * uz;
    if (jac) {
        jac[0] = 2.0 * y0 * ux;
        jac[1] = 2.0 * y1 * ux;
        jac[2] = 2.0 * y1 * uy;
        jac[3] = 2.0 * y2 * ux;
        jac[4] = 2.0 * y2 * uy;
        jac[5] = 2.0 * y2 * uz;
        jac[6] = -2.0 * (p[0] * y0 + p[1] * y1 + p[3] * y2);
        jac[7] = -2.0 * (p[2] * y1 + p[4] * y2);
        jac[8] = -2.0 * (p[5] * y2);
    }
    return y0 * y0 + y1 * y1 + y2 * y2 - g2;
}

static double total_cost(const double p[NP], const vec3_t *a, int n, double g2) {
    double sum = 0.0;
    for (int i = 0; i < n; ++i) {
        double r = residual(p, a[i], g2, NULL);
        sum += r * r;
    }
    return sum;
}

/* Гаус із частковим вибором головного елемента; матриця na×na, права частина в rhs. */
static bool solve_dense(double h[NP][NP], double rhs[NP], int na, double out[NP]) {
    double aug[NP][NP + 1];
    for (int i = 0; i < na; ++i) {
        for (int j = 0; j < na; ++j) aug[i][j] = h[i][j];
        aug[i][na] = rhs[i];
    }
    for (int c = 0; c < na; ++c) {
        int piv = c;
        for (int r = c + 1; r < na; ++r)
            if (fabs(aug[r][c]) > fabs(aug[piv][c])) piv = r;
        if (fabs(aug[piv][c]) < 1e-14) return false;
        if (piv != c) {
            for (int j = c; j <= na; ++j) {
                double t = aug[c][j]; aug[c][j] = aug[piv][j]; aug[piv][j] = t;
            }
        }
        for (int r = c + 1; r < na; ++r) {
            double k = aug[r][c] / aug[c][c];
            if (k == 0.0) continue;
            for (int j = c; j <= na; ++j) aug[r][j] -= k * aug[c][j];
        }
    }
    for (int i = na - 1; i >= 0; --i) {
        double s = aug[i][na];
        for (int j = i + 1; j < na; ++j) s -= aug[i][j] * out[j];
        out[i] = s / aug[i][i];
        if (!isfinite(out[i])) return false;
    }
    return true;
}

/* Усі шість граней мають бути в наборі: інакше еліпсоїд не закріплений по всіх осях. */
static bool faces_covered(const vec3_t *a, int n, float g) {
    float lo[3] = { a[0].x, a[0].y, a[0].z };
    float hi[3] = { a[0].x, a[0].y, a[0].z };
    for (int i = 1; i < n; ++i) {
        const float v[3] = { a[i].x, a[i].y, a[i].z };
        for (int k = 0; k < 3; ++k) {
            if (v[k] < lo[k]) lo[k] = v[k];
            if (v[k] > hi[k]) hi[k] = v[k];
        }
    }
    bool face[6] = { false, false, false, false, false, false };
    for (int i = 0; i < n; ++i) {
        const float v[3] = { a[i].x, a[i].y, a[i].z };
        int dom = 0;
        float best = 0.0f;
        float d[3];
        for (int k = 0; k < 3; ++k) {
            d[k] = v[k] - 0.5f * (lo[k] + hi[k]);
            if (fabsf(d[k]) > best) { best = fabsf(d[k]); dom = k; }
        }
        if (best < 0.5f * g) continue;             /* позиція не притиснута до жодної грані */
        face[2 * dom + (d[dom] > 0.0f ? 0 : 1)] = true;
    }
    for (int k = 0; k < 6; ++k) if (!face[k]) return false;
    return true;
}

calib6_status_t calib6_solve(const vec3_t *avg, int count, float gravity,
                             calib6_model_t model, calib6_result_t *out) {
    if (!avg || !out || count <= 0 || !(gravity > 0.0f) || !isfinite(gravity))
        return CALIB6_ERR_ARGS;
    for (int i = 0; i < count; ++i)
        if (!vec3_is_finite(avg[i])) return CALIB6_ERR_ARGS;

    const int *active = (model == CALIB6_MODEL_TRIAXIAL) ? ACTIVE_FULL : ACTIVE_DIAG;
    const int na = (model == CALIB6_MODEL_TRIAXIAL) ? 9 : 6;
    const int need = (model == CALIB6_MODEL_TRIAXIAL) ? 9 : 6;
    if (count < need) return CALIB6_ERR_FEW_POSITIONS;
    if (!faces_covered(avg, count, gravity)) return CALIB6_ERR_NOT_SPANNING;

    /* Початкове наближення: центр коробки — зсув, півширина — обернений масштаб. */
    float lo[3] = { avg[0].x, avg[0].y, avg[0].z };
    float hi[3] = { avg[0].x, avg[0].y, avg[0].z };
    for (int i = 1; i < count; ++i) {
        const float v[3] = { avg[i].x, avg[i].y, avg[i].z };
        for (int k = 0; k < 3; ++k) {
            if (v[k] < lo[k]) lo[k] = v[k];
            if (v[k] > hi[k]) hi[k] = v[k];
        }
    }
    double p[NP] = { 1.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0 };
    const int diag_idx[3] = { 0, 2, 5 };
    for (int k = 0; k < 3; ++k) {
        double half = 0.5 * ((double)hi[k] - (double)lo[k]);
        if (half < 1e-6) return CALIB6_ERR_NOT_SPANNING;
        p[diag_idx[k]] = (double)gravity / half;
        p[6 + k] = 0.5 * ((double)hi[k] + (double)lo[k]);
    }

    const double g2 = (double)gravity * (double)gravity;
    double lambda = 1e-3;
    double cost = total_cost(p, avg, count, g2);
    int iter = 0;
    bool converged = false;

    for (iter = 0; iter < 100; ++iter) {
        double h[NP][NP];
        double grad[NP];
        memset(h, 0, sizeof(h));
        memset(grad, 0, sizeof(grad));
        for (int i = 0; i < count; ++i) {
            double jac[NP];
            double r = residual(p, avg[i], g2, jac);
            for (int a1 = 0; a1 < na; ++a1) {
                double ja = jac[active[a1]];
                grad[a1] += ja * r;
                for (int a2 = 0; a2 < na; ++a2) h[a1][a2] += ja * jac[active[a2]];
            }
        }
        double damped[NP][NP];
        memcpy(damped, h, sizeof(h));
        for (int a1 = 0; a1 < na; ++a1) damped[a1][a1] *= (1.0 + lambda);

        double rhs[NP], delta[NP];
        for (int a1 = 0; a1 < na; ++a1) rhs[a1] = -grad[a1];
        if (!solve_dense(damped, rhs, na, delta)) return CALIB6_ERR_SINGULAR;

        double trial[NP];
        memcpy(trial, p, sizeof(p));
        for (int a1 = 0; a1 < na; ++a1) trial[active[a1]] += delta[a1];
        double trial_cost = total_cost(trial, avg, count, g2);

        if (isfinite(trial_cost) && trial_cost < cost) {
            double gain = cost - trial_cost;
            memcpy(p, trial, sizeof(p));
            cost = trial_cost;
            lambda = (lambda > 1e-9) ? lambda / 3.0 : lambda;
            if (gain < 1e-12 * (1.0 + cost)) { converged = true; break; }
        } else {
            lambda *= 5.0;
            if (lambda > 1e9) break;   /* крок нікуди не веде — далі лише марні ітерації */
        }
    }
    if (!converged && iter >= 100) return CALIB6_ERR_NO_CONVERGENCE;
    if (!converged) return CALIB6_ERR_NO_CONVERGENCE;

    /* Діагональ M мусить бути додатною: інверсія знака осі — не масштаб, а дзеркало. */
    for (int k = 0; k < 3; ++k)
        if (p[diag_idx[k]] <= 0.0) return CALIB6_ERR_SINGULAR;

    mat3_t m = { { { (float)p[0], 0.0f,        0.0f        },
                   { (float)p[1], (float)p[2], 0.0f        },
                   { (float)p[3], (float)p[4], (float)p[5] } } };
    out->m = m;
    out->bias = vec3_make((float)p[6], (float)p[7], (float)p[8]);
    out->iterations = iter + 1;

    double acc = 0.0;
    for (int i = 0; i < count; ++i) {
        vec3_t y = mat3_mul_vec3(out->m, vec3_sub(avg[i], out->bias));
        double e = (double)vec3_norm(y) - (double)gravity;
        acc += e * e;
    }
    out->rms_rel = (float)(sqrt(acc / count) / gravity);
    return CALIB6_OK;
}

bool calib6_still_average(const vec3_t *samples, int count, float tol, vec3_t *out_avg) {
    if (!samples || !out_avg || count < 2 || !(tol > 0.0f)) return false;
    vec3_t sum = vec3_zero();
    for (int i = 0; i < count; ++i) {
        if (!vec3_is_finite(samples[i])) return false;
        sum = vec3_add(sum, samples[i]);
    }
    vec3_t mean = vec3_scale(sum, 1.0f / (float)count);
    float worst = 0.0f;
    for (int i = 0; i < count; ++i) {
        float d = vec3_norm(vec3_sub(samples[i], mean));
        if (d > worst) worst = d;
    }
    *out_avg = mean;
    return worst <= tol;   /* апарат ворухнувся — позицію переписуємо, а не «зате швидко» */
}
