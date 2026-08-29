#include "ekf_dr.h"

#include <math.h>
#include <string.h>

/* ── Арифметика 3x3 ──────────────────────────────────────────────────────
   Блокова структура коваріації (позиція, швидкість, зсув) робить усю
   екстраполяцію набором дій над матрицями 3x3. Окремої бібліотеки під це
   заводити немає сенсу: потрібні рівно шість операцій, усі на стеку. */

typedef float mat3[3][3];

static void m_copy(mat3 dst, const float src[3][3])
{
    memcpy(dst, src, sizeof(mat3));
}

static void m_transpose(mat3 out, const float a[3][3])
{
    for (int i = 0; i < 3; i++) {
        for (int j = 0; j < 3; j++) out[i][j] = a[j][i];
    }
}

static void m_scale(mat3 out, const float a[3][3], float k)
{
    for (int i = 0; i < 3; i++) {
        for (int j = 0; j < 3; j++) out[i][j] = a[i][j] * k;
    }
}

static void m_addto(mat3 acc, const float m[3][3])
{
    for (int i = 0; i < 3; i++) {
        for (int j = 0; j < 3; j++) acc[i][j] += m[i][j];
    }
}

/* out = a · b. Вхід і вихід можуть збігатися — результат збирається в
   тимчасовій копії. */
static void m_mul(mat3 out, const float a[3][3], const float b[3][3])
{
    mat3 t;
    for (int i = 0; i < 3; i++) {
        for (int j = 0; j < 3; j++) {
            float acc = 0.0f;
            for (int k = 0; k < 3; k++) acc += a[i][k] * b[k][j];
            t[i][j] = acc;
        }
    }
    m_copy(out, t);
}

/* out = a · bᵀ — окремо, бо в екстраполяції P транспонування трапляється
   частіше за саме множення, і зайва копія тут не потрібна. */
static void m_mul_t(mat3 out, const float a[3][3], const float b[3][3])
{
    mat3 t;
    for (int i = 0; i < 3; i++) {
        for (int j = 0; j < 3; j++) {
            float acc = 0.0f;
            for (int k = 0; k < 3; k++) acc += a[i][k] * b[j][k];
            t[i][j] = acc;
        }
    }
    m_copy(out, t);
}

void ekf_rotate(float out[3], const float R[3][3], const float v[3])
{
    float t[3];
    for (int i = 0; i < 3; i++) {
        t[i] = R[i][0] * v[0] + R[i][1] * v[1] + R[i][2] * v[2];
    }
    for (int i = 0; i < 3; i++) out[i] = t[i];
}

bool ekf_vec3_finite(const float v[3])
{
    return isfinite(v[0]) && isfinite(v[1]) && isfinite(v[2]);
}

bool ekf_is_rotation(const float R[3][3], float tol)
{
    for (int i = 0; i < 3; i++) {
        for (int j = 0; j < 3; j++) {
            if (!isfinite(R[i][j])) return false;
        }
    }

    /* Стовпці одиничної довжини й попарно ортогональні. Двох перевірок
       вистачає: третій стовпець ортонормальної матриці визначений двома
       першими, і якщо він зіпсований — це видно з норми. */
    for (int c = 0; c < 3; c++) {
        float n = 0.0f;
        for (int i = 0; i < 3; i++) n += R[i][c] * R[i][c];
        if (fabsf(n - 1.0f) > tol) return false;
    }
    for (int a = 0; a < 3; a++) {
        for (int b = a + 1; b < 3; b++) {
            float d = 0.0f;
            for (int i = 0; i < 3; i++) d += R[i][a] * R[i][b];
            if (fabsf(d) > tol) return false;
        }
    }
    return true;
}

/* ── Блокові доступи до коваріації ───────────────────────────────────────
   P розбита на дев'ять блоків 3x3: позиція (p), швидкість (v), зсув (b).
   Уся екстраполяція нижче написана саме в блоках — так видно структуру
   матриці переходу, і жодного множення на нуль не виконується. */

static void blk_get(const float P[EKF_DR_N][EKF_DR_N], int r, int c, mat3 out)
{
    for (int i = 0; i < 3; i++) {
        for (int j = 0; j < 3; j++) out[i][j] = P[r + i][c + j];
    }
}

static void blk_set(float P[EKF_DR_N][EKF_DR_N], int r, int c, const float m[3][3])
{
    for (int i = 0; i < 3; i++) {
        for (int j = 0; j < 3; j++) P[r + i][c + j] = m[i][j];
    }
}

/* Кладе блок m у позицію (r,c) і його транспозицію у дзеркальну (c,r):
   коваріація симетрична, зберігаємо це точно, а не «майже». */
static void blk_set_sym(float P[EKF_DR_N][EKF_DR_N], int r, int c, const float m[3][3])
{
    mat3 mt;
    blk_set(P, r, c, m);
    m_transpose(mt, m);
    blk_set(P, c, r, mt);
}

/* ── Гігієна коваріації ──────────────────────────────────────────────────
   Три різні хвороби float32, і кожна лікується окремо.

   1. Асиметрія. (I − KH)P математично симетрична, у машинній арифметиці —
      ні. Розбіжність P[i][j] і P[j][i] росте від кроку до кроку й зрештою
      робить матрицю невід'ємно невизначеною.
   2. Колапс діагоналі. Дисперсія, підтиснута до нуля (або до від'ємного
      значення через округлення), означає K → 0: фільтр перестає слухати
      давачі й назавжди застигає на своїй помилковій оцінці.
   3. Розліт кореляцій. |P[i][j]| не може перевищувати √(P[i][i]·P[j][j]);
      якщо перевищив — це вже не коваріація, і наступний крок дасть
      від'ємну інноваційну дисперсію. */
static void ekf_condition(ekf_dr_t *ekf)
{
    /* 1 — симетризація. */
    for (int i = 0; i < EKF_DR_N; i++) {
        for (int j = i + 1; j < EKF_DR_N; j++) {
            float avg = 0.5f * (ekf->P[i][j] + ekf->P[j][i]);
            if (!isfinite(avg)) avg = 0.0f;
            ekf->P[i][j] = avg;
            ekf->P[j][i] = avg;
        }
    }

    /* 2 — затиск діагоналі знизу й зверху. */
    for (int i = 0; i < EKF_DR_N; i++) {
        if (!isfinite(ekf->P[i][i]) || ekf->P[i][i] < ekf->p_min) {
            ekf->P[i][i] = ekf->p_min;
            ekf->n_reset++;
        } else if (ekf->P[i][i] > ekf->p_max) {
            ekf->P[i][i] = ekf->p_max;
        }
    }

    /* 3 — обмеження позадіагональних елементів нерівністю Коші—Буняковського. */
    for (int i = 0; i < EKF_DR_N; i++) {
        for (int j = i + 1; j < EKF_DR_N; j++) {
            float lim = sqrtf(ekf->P[i][i] * ekf->P[j][j]);
            if (ekf->P[i][j] > lim) {
                ekf->P[i][j] = ekf->P[j][i] = lim;
            } else if (ekf->P[i][j] < -lim) {
                ekf->P[i][j] = ekf->P[j][i] = -lim;
            }
        }
    }

    /* Стан теж має лишатися фізичним: зсув нуля акселерометра в межах
       паспорта давача. Якщо оцінка вперлася в межу — це майже завжди
       ознака похибки орієнтації, яку фільтр намагається списати на зсув. */
    for (int i = EKF_BAX; i <= EKF_BAZ; i++) {
        if (!isfinite(ekf->x[i])) {
            ekf->x[i] = 0.0f;
            ekf->n_reset++;
        } else if (ekf->x[i] > ekf->bias_max) {
            ekf->x[i] = ekf->bias_max;
        } else if (ekf->x[i] < -ekf->bias_max) {
            ekf->x[i] = -ekf->bias_max;
        }
    }
}

void ekf_dr_init(ekf_dr_t *ekf)
{
    memset(ekf, 0, sizeof(*ekf));

    /* Початкова невизначеність: координата ±1 м, швидкість ±0.1 м/с,
       зсув акселерометра ±0.05 м/с² (типове залишкове після заводського
       калібрування MEMS-акселерометра середнього класу). */
    for (int i = EKF_PX; i <= EKF_PZ; i++) ekf->P[i][i] = 1.0f;
    for (int i = EKF_VX; i <= EKF_VZ; i++) ekf->P[i][i] = 0.01f;
    for (int i = EKF_BAX; i <= EKF_BAZ; i++) ekf->P[i][i] = 0.0025f;

    ekf->q_pos = 1.0e-3f;
    ekf->q_vel = 5.0e-2f;
    ekf->q_bias = 1.0e-5f;

    ekf->p_min = 1.0e-6f;
    ekf->p_max = 1.0e4f;
    ekf->bias_max = 0.5f;
}

bool ekf_dr_predict(ekf_dr_t *ekf, const float a_body[3], const float R_wb[3][3], float dt)
{
    /* Вхідний контроль. Оцінювач орієнтації після втрати кватерніона віддає
       NaN, а драйвер IMU при збої SPI — нулі або старий буфер; жодне з цього
       не має права дійти до коваріації. */
    if (!(dt > 0.0f) || dt > 0.1f) return false;
    if (!ekf_vec3_finite(a_body)) return false;
    if (!ekf_is_rotation(R_wb, 1.0e-2f)) return false;

    /* ── 1. Компенсація оціненого зсуву нуля ── */
    float a_unbiased[3];
    for (int i = 0; i < 3; i++) a_unbiased[i] = a_body[i] - ekf->x[EKF_BAX + i];

    /* ── 2. Поворот у світ і додавання гравітації ──
       Акселерометр міряє питому силу; у спокої це −g уздовж осі «вниз»,
       тому додавання +g повертає нам справжнє прискорення руху. */
    float a_world[3];
    ekf_rotate(a_world, R_wb, a_unbiased);
    a_world[2] += EKF_GRAVITY_MSS;

    /* ── 3. Кінематична інтеграція ── */
    const float dt2 = 0.5f * dt * dt;
    for (int i = 0; i < 3; i++) {
        ekf->x[EKF_PX + i] += ekf->x[EKF_VX + i] * dt + a_world[i] * dt2;
        ekf->x[EKF_VX + i] += a_world[i] * dt;
    }

    /* ── 4. Екстраполяція коваріації: P = F·P·Fᵀ + Q·dt ──

       Матриця переходу в блоках (I — одинична 3x3):

           F = [ I   I·dt   A ]        A = −0.5·dt²·R_wb
               [ 0   I      B ]        B = −dt·R_wb
               [ 0   0      I ]

       Блоки A і B — це похідні координати й швидкості по зсуву: зсув
       входить у прискорення зі знаком «мінус» і повертається у світ тією
       самою матрицею R_wb. Саме через них у P з'являються кореляції
       швидкість↔зсув, без яких оптичний потік ніколи не «навчив» би
       фільтр зсуву нуля. */
    mat3 Ppp, Ppv, Ppb, Pvv, Pvb, Pbb;
    blk_get(ekf->P, 0, 0, Ppp);
    blk_get(ekf->P, 0, 3, Ppv);
    blk_get(ekf->P, 0, 6, Ppb);
    blk_get(ekf->P, 3, 3, Pvv);
    blk_get(ekf->P, 3, 6, Pvb);
    blk_get(ekf->P, 6, 6, Pbb);

    mat3 A, B;
    m_scale(A, R_wb, -dt2);
    m_scale(B, R_wb, -dt);

    mat3 PpvT, PpbT, PvbT;
    m_transpose(PpvT, Ppv);
    m_transpose(PpbT, Ppb);
    m_transpose(PvbT, Pvb);

    mat3 tmp;

    /* T = F·P — потрібні лише рядки p та v, рядок b лишається як був. */
    mat3 T1p, T1v, T1b, T2v, T2b;

    m_copy(T1p, Ppp);                        /* T1p = Ppp + dt·Pvp + A·Pbp */
    m_scale(tmp, PpvT, dt);   m_addto(T1p, tmp);
    m_mul(tmp, A, PpbT);      m_addto(T1p, tmp);

    m_copy(T1v, Ppv);                        /* T1v = Ppv + dt·Pvv + A·Pbv */
    m_scale(tmp, Pvv, dt);    m_addto(T1v, tmp);
    m_mul(tmp, A, PvbT);      m_addto(T1v, tmp);

    m_copy(T1b, Ppb);                        /* T1b = Ppb + dt·Pvb + A·Pbb */
    m_scale(tmp, Pvb, dt);    m_addto(T1b, tmp);
    m_mul(tmp, A, Pbb);       m_addto(T1b, tmp);

    m_copy(T2v, Pvv);                        /* T2v = Pvv + B·Pbv */
    m_mul(tmp, B, PvbT);      m_addto(T2v, tmp);

    m_copy(T2b, Pvb);                        /* T2b = Pvb + B·Pbb */
    m_mul(tmp, B, Pbb);       m_addto(T2b, tmp);

    /* P' = T·Fᵀ */
    mat3 Npp, Npv, Npb, Nvv, Nvb;

    m_copy(Npp, T1p);                        /* Npp = T1p + dt·T1v + T1b·Aᵀ */
    m_scale(tmp, T1v, dt);    m_addto(Npp, tmp);
    m_mul_t(tmp, T1b, A);     m_addto(Npp, tmp);

    m_copy(Npv, T1v);                        /* Npv = T1v + T1b·Bᵀ */
    m_mul_t(tmp, T1b, B);     m_addto(Npv, tmp);

    m_copy(Npb, T1b);                        /* Npb = T1b */

    m_copy(Nvv, T2v);                        /* Nvv = T2v + T2b·Bᵀ */
    m_mul_t(tmp, T2b, B);     m_addto(Nvv, tmp);

    m_copy(Nvb, T2b);                        /* Nvb = T2b, Nbb = Pbb */

    /* + Q·dt: шум процесу входить лише в діагональ блоків. */
    for (int i = 0; i < 3; i++) {
        Npp[i][i] += ekf->q_pos * dt;
        Nvv[i][i] += ekf->q_vel * dt;
        Pbb[i][i] += ekf->q_bias * dt;
    }

    blk_set(ekf->P, 0, 0, Npp);
    blk_set_sym(ekf->P, 0, 3, Npv);
    blk_set_sym(ekf->P, 0, 6, Npb);
    blk_set(ekf->P, 3, 3, Nvv);
    blk_set_sym(ekf->P, 3, 6, Nvb);
    blk_set(ekf->P, 6, 6, Pbb);

    ekf_condition(ekf);
    return true;
}

ekf_result_t ekf_dr_fuse_scalar(ekf_dr_t *ekf, const float H[EKF_DR_N],
                                float z, float r, float gate, float *d2_out)
{
    if (d2_out) *d2_out = 0.0f;

    if (!isfinite(z) || !isfinite(r) || !(r > 0.0f)) {
        ekf->n_numeric++;
        return EKF_REJECT_NUMERIC;
    }

    /* PHᵀ — вектор 9x1, спільний і для S, і для коефіцієнта Калмана. */
    float PHt[EKF_DR_N];
    for (int i = 0; i < EKF_DR_N; i++) {
        float acc = 0.0f;
        for (int j = 0; j < EKF_DR_N; j++) acc += ekf->P[i][j] * H[j];
        PHt[i] = acc;
    }

    float S = r;                                  /* S = H·P·Hᵀ + R */
    float Hx = 0.0f;
    for (int j = 0; j < EKF_DR_N; j++) {
        S += H[j] * PHt[j];
        Hx += H[j] * ekf->x[j];
    }

    if (!isfinite(S) || S <= 0.0f) {
        /* Коваріація зіпсована настільки, що дисперсія інновації не додатна.
           Єдине чесне, що тут можна зробити, — не чіпати стан. Гігієна
           витягне діагональ, а наступні вимірювання відновлять довіру. */
        ekf->n_numeric++;
        ekf_condition(ekf);
        return EKF_REJECT_NUMERIC;
    }

    const float y = z - Hx;                       /* інновація (нев'язка) */
    const float d2 = (y * y) / S;                 /* квадрат відстані Махаланобіса */
    if (d2_out) *d2_out = d2;

    if (gate > 0.0f && d2 > gate) {
        ekf->n_gated++;
        return EKF_REJECT_GATE;
    }

    /* K = P·Hᵀ·S⁻¹; для скаляра S⁻¹ — це просто ділення. */
    float K[EKF_DR_N];
    for (int i = 0; i < EKF_DR_N; i++) K[i] = PHt[i] / S;

    for (int i = 0; i < EKF_DR_N; i++) ekf->x[i] += K[i] * y;

    /* P = (I − K·H)·P. Оскільки (K·H)·P = K·(H·P) = K·(PHᵀ)ᵀ для симетричної
       P, увесь крок — це одне зовнішнє множення векторів. */
    for (int i = 0; i < EKF_DR_N; i++) {
        for (int j = 0; j < EKF_DR_N; j++) {
            ekf->P[i][j] -= K[i] * PHt[j];
        }
    }

    ekf_condition(ekf);
    return EKF_FUSED;
}

ekf_result_t ekf_dr_update_velocity2d(ekf_dr_t *ekf, float vx_meas, float vy_meas,
                                      float r_cov, float gate)
{
    ekf_result_t worst = EKF_FUSED;

    const float z[2] = {vx_meas, vy_meas};
    const int idx[2] = {EKF_VX, EKF_VY};

    for (int axis = 0; axis < 2; axis++) {
        float H[EKF_DR_N] = {0};
        H[idx[axis]] = 1.0f;                      /* H_vel = [0₃ | e_axis | 0₃] */

        ekf_result_t res = ekf_dr_fuse_scalar(ekf, H, z[axis], r_cov, gate, NULL);
        if (res != EKF_FUSED && worst == EKF_FUSED) worst = res;
    }
    return worst;
}

ekf_result_t ekf_dr_update_altitude(ekf_dr_t *ekf, float pz_meas, float r_cov, float gate)
{
    float H[EKF_DR_N] = {0};
    H[EKF_PZ] = 1.0f;                             /* H_alt = [0 0 1 | 0₃ | 0₃] */
    return ekf_dr_fuse_scalar(ekf, H, pz_meas, r_cov, gate, NULL);
}

ekf_result_t ekf_dr_update_zupt(ekf_dr_t *ekf, float r_zupt)
{
    ekf_result_t worst = EKF_FUSED;

    for (int axis = 0; axis < 3; axis++) {
        float H[EKF_DR_N] = {0};
        H[EKF_VX + axis] = 1.0f;

        /* Строб ширший, ніж для потоку (5σ): детектор нерухомості іноді
           спрацьовує на кінці гальмування, і жорсткий строб тоді просто
           викидав би найцінніше вимірювання. */
        ekf_result_t res = ekf_dr_fuse_scalar(ekf, H, 0.0f, r_zupt, 25.0f, NULL);
        if (res != EKF_FUSED && worst == EKF_FUSED) worst = res;
    }
    return worst;
}

void ekf_dr_get_state(const ekf_dr_t *ekf, float pos[3], float vel[3], float bias[3])
{
    for (int i = 0; i < 3; i++) {
        if (pos) pos[i] = ekf->x[EKF_PX + i];
        if (vel) vel[i] = ekf->x[EKF_VX + i];
        if (bias) bias[i] = ekf->x[EKF_BAX + i];
    }
}

float ekf_dr_pos_sigma(const ekf_dr_t *ekf, int axis)
{
    return sqrtf(ekf->P[EKF_PX + axis][EKF_PX + axis]);
}

float ekf_dr_vel_sigma(const ekf_dr_t *ekf, int axis)
{
    return sqrtf(ekf->P[EKF_VX + axis][EKF_VX + axis]);
}
