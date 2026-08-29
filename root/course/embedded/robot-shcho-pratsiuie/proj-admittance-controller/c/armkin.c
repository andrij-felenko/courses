#include "armkin.h"

#include <math.h>
#include <string.h>

#define ARM_HALF_PI 1.57079632679f

/* Демонстраційна антропоморфна рука: плече, лікоть, сферичне зап'ястя. */
const arm_link_t ARM_DEMO_LINKS[ARM_JOINTS] = {
    { 0.000f,  ARM_HALF_PI, 0.330f, 0.0f },
    { 0.340f,  0.0f,        0.000f, 0.0f },
    { 0.040f,  ARM_HALF_PI, 0.000f, 0.0f },
    { 0.000f, -ARM_HALF_PI, 0.320f, 0.0f },
    { 0.000f,  ARM_HALF_PI, 0.000f, 0.0f },
    { 0.000f,  0.0f,        0.090f, 0.0f },
};

static void mat4_identity(float t[16])
{
    for (int i = 0; i < 16; ++i) {
        t[i] = 0.0f;
    }
    t[0] = t[5] = t[10] = t[15] = 1.0f;
}

static void mat4_mul(const float a[16], const float b[16], float out[16])
{
    for (int r = 0; r < 4; ++r) {
        for (int c = 0; c < 4; ++c) {
            float s = 0.0f;
            for (int k = 0; k < 4; ++k) {
                s += a[r * 4 + k] * b[k * 4 + c];
            }
            out[r * 4 + c] = s;
        }
    }
}

static void link_transform(const arm_link_t *lk, float theta, float t[16])
{
    const float ct = cosf(theta), st = sinf(theta);
    const float ca = cosf(lk->alpha), sa = sinf(lk->alpha);

    t[0] = ct; t[1] = -st * ca; t[2] = st * sa;   t[3] = lk->a * ct;
    t[4] = st; t[5] = ct * ca;  t[6] = -ct * sa;  t[7] = lk->a * st;
    t[8] = 0.0f; t[9] = sa;     t[10] = ca;       t[11] = lk->d;
    t[12] = 0.0f; t[13] = 0.0f; t[14] = 0.0f;     t[15] = 1.0f;
}

static void cross3(const float a[3], const float b[3], float out[3])
{
    out[0] = a[1] * b[2] - a[2] * b[1];
    out[1] = a[2] * b[0] - a[0] * b[2];
    out[2] = a[0] * b[1] - a[1] * b[0];
}

/* A = J·Jᵀ — симетрична 6×6, ядро і маніпульованості, і DLS. */
static void jacobian_gram(const float jac[CART_DOF][ARM_JOINTS], float a[CART_DOF][CART_DOF])
{
    for (int r = 0; r < CART_DOF; ++r) {
        for (int c = 0; c < CART_DOF; ++c) {
            float s = 0.0f;
            for (int k = 0; k < ARM_JOINTS; ++k) {
                s += jac[r][k] * jac[c][k];
            }
            a[r][c] = s;
        }
    }
}

/* Розклад Холецького A = L·Lᵀ. false — матриця не додатно визначена,
   тобто рука фактично сидить у сингулярності. */
static bool cholesky6(const float a[CART_DOF][CART_DOF], float l[CART_DOF][CART_DOF])
{
    for (int j = 0; j < CART_DOF; ++j) {
        float diag = a[j][j];
        for (int k = 0; k < j; ++k) {
            diag -= l[j][k] * l[j][k];
        }
        if (diag <= 1.0e-12f) {
            return false;
        }
        l[j][j] = sqrtf(diag);
        for (int i = j + 1; i < CART_DOF; ++i) {
            float s = a[i][j];
            for (int k = 0; k < j; ++k) {
                s -= l[i][k] * l[j][k];
            }
            l[i][j] = s / l[j][j];
            l[j][i] = 0.0f;
        }
    }
    return true;
}

static void cholesky_solve(const float l[CART_DOF][CART_DOF], const float b[CART_DOF], float x[CART_DOF])
{
    float y[CART_DOF];
    for (int i = 0; i < CART_DOF; ++i) { /* прямий хід: L·y = b */
        float s = b[i];
        for (int k = 0; k < i; ++k) {
            s -= l[i][k] * y[k];
        }
        y[i] = s / l[i][i];
    }
    for (int i = CART_DOF - 1; i >= 0; --i) { /* зворотний хід: Lᵀ·x = y */
        float s = y[i];
        for (int k = i + 1; k < CART_DOF; ++k) {
            s -= l[k][i] * x[k];
        }
        x[i] = s / l[i][i];
    }
}

void arm_forward(const arm_link_t links[ARM_JOINTS], const float q[ARM_JOINTS], arm_state_t *st)
{
    if (!links || !q || !st) {
        return;
    }

    float t[16];
    mat4_identity(t);

    float axis[ARM_JOINTS][3];   /* осі обертання суглобів у базі */
    float origin[ARM_JOINTS][3]; /* початки систем суглобів у базі */

    for (int i = 0; i < ARM_JOINTS; ++i) {
        /* Вісь суглоба i — це z системи i−1, тобто третій стовпець T. */
        axis[i][0] = t[2];  axis[i][1] = t[6];  axis[i][2] = t[10];
        origin[i][0] = t[3]; origin[i][1] = t[7]; origin[i][2] = t[11];

        float a_i[16], next[16];
        link_transform(&links[i], q[i] + links[i].theta_offset, a_i);
        mat4_mul(t, a_i, next);
        memcpy(t, next, sizeof next);
    }

    st->p_flange[0] = t[3];
    st->p_flange[1] = t[7];
    st->p_flange[2] = t[11];

    st->r_flange[0] = t[0]; st->r_flange[1] = t[1]; st->r_flange[2] = t[2];
    st->r_flange[3] = t[4]; st->r_flange[4] = t[5]; st->r_flange[5] = t[6];
    st->r_flange[6] = t[8]; st->r_flange[7] = t[9]; st->r_flange[8] = t[10];

    /* Стовпець обертального суглоба: лінійна частина z × (p_e − p_i),
       кутова — сама вісь z. */
    for (int i = 0; i < ARM_JOINTS; ++i) {
        const float arm_vec[3] = {
            st->p_flange[0] - origin[i][0],
            st->p_flange[1] - origin[i][1],
            st->p_flange[2] - origin[i][2],
        };
        float lin[3];
        cross3(axis[i], arm_vec, lin);
        for (int r = 0; r < 3; ++r) {
            st->jac[r][i] = lin[r];
            st->jac[3 + r][i] = axis[i][r];
        }
    }

    /* w = sqrt(det(J·Jᵀ)) = добуток діагоналі L. Не розклалося — нуль,
       тобто рука вже втратила напрямок руху. */
    float gram[CART_DOF][CART_DOF], l[CART_DOF][CART_DOF];
    jacobian_gram(st->jac, gram);
    if (cholesky6(gram, l)) {
        float w = 1.0f;
        for (int i = 0; i < CART_DOF; ++i) {
            w *= l[i][i];
        }
        st->manipulability = w;
    } else {
        st->manipulability = 0.0f;
    }
}

void arm_rotate6(const float r_flange[9], const float body[CART_DOF], float base[CART_DOF])
{
    if (!r_flange || !body || !base) {
        return;
    }
    for (int half = 0; half < 2; ++half) {
        const int o = half * 3;
        for (int i = 0; i < 3; ++i) {
            base[o + i] = r_flange[3 * i] * body[o] +
                          r_flange[3 * i + 1] * body[o + 1] +
                          r_flange[3 * i + 2] * body[o + 2];
        }
    }
}

/* Рівномірне масштабування зберігає НАПРЯМОК руху: різати кожну вісь
   окремо означало б поїхати не туди, куди наказано. */
static void clamp_joint_rate(float q_dot[ARM_JOINTS])
{
    float peak = 0.0f;
    for (int j = 0; j < ARM_JOINTS; ++j) {
        const float v = fabsf(q_dot[j]);
        if (v > peak) {
            peak = v;
        }
    }
    if (peak > ARM_MAX_JOINT_RATE) {
        const float scale = ARM_MAX_JOINT_RATE / peak;
        for (int j = 0; j < ARM_JOINTS; ++j) {
            q_dot[j] *= scale;
        }
    }
}

bool arm_dls_joint_velocity(const arm_state_t *st, const float v_cmd[CART_DOF],
                            float lambda_max, float w_threshold,
                            float q_dot[ARM_JOINTS], float *lambda_used)
{
    if (!st || !v_cmd || !q_dot || !(lambda_max >= 0.0f) || !(w_threshold > 0.0f)) {
        return false;
    }

    /* У зручній робочій зоні демпфування нульове — псевдоінверсія точна.
       Ближче до сингулярності lambda росте квадратично, м'яко жертвуючи
       точністю відпрацювання швидкості заради скінченних обертів моторів. */
    float lambda = 0.0f;
    if (st->manipulability < w_threshold) {
        const float k = 1.0f - st->manipulability / w_threshold;
        lambda = lambda_max * k * k;
    }

    float l[CART_DOF][CART_DOF];
    bool ok = false;
    for (int attempt = 0; attempt < 5 && !ok; ++attempt) {
        float a[CART_DOF][CART_DOF];
        jacobian_gram(st->jac, a);
        for (int i = 0; i < CART_DOF; ++i) {
            a[i][i] += lambda * lambda;
        }
        ok = cholesky6(a, l);
        if (!ok) {
            /* Числова обробка вже після регуляризації: піднімаємо демпфування,
               доки розклад не пройде. Краще неточна швидкість, ніж NaN у CAN. */
            lambda = (lambda > 0.0f) ? lambda * 2.0f : lambda_max;
        }
    }
    if (!ok) {
        return false;
    }

    float y[CART_DOF];
    cholesky_solve(l, v_cmd, y);
    for (int j = 0; j < ARM_JOINTS; ++j) {
        float s = 0.0f;
        for (int i = 0; i < CART_DOF; ++i) {
            s += st->jac[i][j] * y[i];
        }
        q_dot[j] = s;
    }
    clamp_joint_rate(q_dot);

    if (lambda_used) {
        *lambda_used = lambda;
    }
    return true;
}
