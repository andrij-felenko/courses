/* main.c — прогін навігаційного модуля на синтетичному польоті.

   На апараті цього файла немає: там ті самі виклики роблять дві задачі
   FreeRTOS — високопріоритетна за перериванням готовності IMU (500 Гц) і
   фонова задача давачів (50 Гц потік, 20 Гц далекомір). Тут вони зведені
   в один цикл, щоб було видно час і порядок подій.

   Прогін показує те, заради чого фільтр і будувався: як швидко відлітає
   чиста інерціальна навігація і скільки з цього відльоту знімають
   оптичний потік, далекомір і ZUPT. Істина відома точно, тому похибку
   оцінки тут не вгадують, а рахують. */

#include "ekf_dr.h"
#include "flow.h"

#include <math.h>
#include <stdatomic.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

#define DT_S             0.002f     /* 500 Гц — крок IMU */
#define DT_US            2000u
#define STEPS            30000u     /* 60 секунд */
#define FLOW_EVERY       10u        /* 50 Гц */
#define RANGE_EVERY      25u        /* 20 Гц */
#define FLOW_LATENCY_US  20000u     /* кадр описує момент 20 мс тому */
#define RANGE_LATENCY_US 5000u
#define REPORT_EVERY     2500u      /* рядок звіту раз на 5 с */

/* Паспортна стала PMW3901, та сама, що в модулі потоку. Якби вони
   розійшлися, фільтр дістав би систематичний масштабний коефіцієнт у
   швидкості — це і є найчастіша причина «потік недооцінює швидкість». */
#define RAD_PER_PIXEL ((float)(42.0 * M_PI / 180.0 / 35.0))

/* Шуми давачів — приблизно рівень ICM-42688 і PMW3901. */
#define ACC_NOISE   0.06f           /* м/с² */
#define GYRO_NOISE  0.003f          /* рад/с */
#define FLOW_NOISE  0.35f           /* пікселів на кадр */
#define RANGE_NOISE 0.012f          /* м */

/* ── Генератор шуму ──────────────────────────────────────────────────────
   xorshift32 плюс перетворення Бокса—Мюллера. Детермінований: прогін
   відтворюваний до біта, і два запуски можна порівнювати. */

static uint32_t rng_state = 20240917u;

static float rng_uniform(void)
{
    rng_state ^= rng_state << 13;
    rng_state ^= rng_state >> 17;
    rng_state ^= rng_state << 5;
    return (float)(rng_state >> 8) / 16777216.0f;
}

static float rng_gauss(void)
{
    static float spare;
    static bool has_spare;

    if (has_spare) {
        has_spare = false;
        return spare;
    }

    float u, v, s;
    do {
        u = 2.0f * rng_uniform() - 1.0f;
        v = 2.0f * rng_uniform() - 1.0f;
        s = u * u + v * v;
    } while (s >= 1.0f || s == 0.0f);

    const float k = sqrtf(-2.0f * logf(s) / s);
    spare = v * k;
    has_spare = true;
    return u * k;
}

/* ── Істина ──────────────────────────────────────────────────────────────
   Дві ділянки польоту, розділені зупинками. Переходи згладжені, щоб
   прискорення лишалося скінченним: стрибок швидкості означав би
   нескінченне прискорення, а акселерометр такого не показав би.
   Зупинки тут не для краси — без них не видно ні детектора нерухомості,
   ні того, як ZUPT витягує зсув нуля акселерометра. */

typedef struct {
    float t;
    float pos[3];                /* істинна позиція NED, м (z вниз) */
    float vel[3];
    float acc[3];
    float R_wb[3][3];
    float gyro[3];
    bool stationary;

    /* Систематичні похибки давачів, які фільтр має вивести сам. */
    float acc_bias[3];
    float gyro_bias[3];

    uint32_t flow_frames;
    uint32_t range_reads;
} truth_t;

static float smoothstep(float a, float b, float t)
{
    if (t <= a) return 0.0f;
    if (t >= b) return 1.0f;
    const float x = (t - a) / (b - a);
    return x * x * (3.0f - 2.0f * x);
}

static float motion_gate(float t)
{
    const float leg1 = smoothstep(4.0f, 5.5f, t) * (1.0f - smoothstep(22.5f, 24.0f, t));
    const float leg2 = smoothstep(30.0f, 31.5f, t) * (1.0f - smoothstep(52.5f, 54.0f, t));
    return leg1 + leg2;
}

static void vel_profile(float t, float v[3])
{
    const float g = motion_gate(t);
    v[0] = g * (1.20f + 0.40f * sinf(0.25f * t));
    v[1] = g * (0.60f * sinf(0.15f * t));
    v[2] = g * (0.15f * sinf(0.50f * t));
}

static void rpy_profile(float t, float rpy[3])
{
    const float g = motion_gate(t);
    rpy[0] = g * 0.12f * sinf(0.70f * t);            /* крен */
    rpy[1] = g * 0.09f * sinf(0.50f * t + 1.0f);     /* тангаж */
    rpy[2] = g * 0.30f * sinf(0.10f * t);            /* курс */
}

/* R = Rz(курс)·Ry(тангаж)·Rx(крен) — класичний порядок для NED. */
static void rpy_to_R(const float rpy[3], float R[3][3])
{
    const float cr = cosf(rpy[0]), sr = sinf(rpy[0]);
    const float cp = cosf(rpy[1]), sp = sinf(rpy[1]);
    const float cy = cosf(rpy[2]), sy = sinf(rpy[2]);

    R[0][0] = cy * cp;
    R[0][1] = cy * sp * sr - sy * cr;
    R[0][2] = cy * sp * cr + sy * sr;
    R[1][0] = sy * cp;
    R[1][1] = sy * sp * sr + cy * cr;
    R[1][2] = sy * sp * cr - cy * sr;
    R[2][0] = -sp;
    R[2][1] = cp * sr;
    R[2][2] = cp * cr;
}

static void transpose(float out[3][3], const float a[3][3])
{
    for (int i = 0; i < 3; i++) {
        for (int j = 0; j < 3; j++) out[i][j] = a[j][i];
    }
}

/* Кутова швидкість тіла з похідної матриці повороту: Ω = Rᵀ·Ṙ —
   кососиметрична, і з неї прямо читаються p, q, r. Числова похідна тут
   дешевша й надійніша за виведення формул переходу від похідних кутів
   Ейлера, а точності 1e-4 с вистачає з величезним запасом. */
static void gyro_at(float t, float out[3])
{
    const float h = 1.0e-4f;
    float rpy_a[3], rpy_b[3], rpy_now[3];
    float Ra[3][3], Rb[3][3], Rt[3][3], RtT[3][3], Rdot[3][3];

    rpy_profile(t - h, rpy_a);
    rpy_profile(t + h, rpy_b);
    rpy_profile(t, rpy_now);
    rpy_to_R(rpy_a, Ra);
    rpy_to_R(rpy_b, Rb);
    rpy_to_R(rpy_now, Rt);
    transpose(RtT, Rt);

    for (int i = 0; i < 3; i++) {
        for (int j = 0; j < 3; j++) Rdot[i][j] = (Rb[i][j] - Ra[i][j]) / (2.0f * h);
    }

    /* Ω = RtT · Rdot, беремо лише три незалежні елементи. */
    float Om[3][3];
    for (int i = 0; i < 3; i++) {
        for (int j = 0; j < 3; j++) {
            float acc = 0.0f;
            for (int k = 0; k < 3; k++) acc += RtT[i][k] * Rdot[k][j];
            Om[i][j] = acc;
        }
    }

    out[0] = Om[2][1];
    out[1] = Om[0][2];
    out[2] = Om[1][0];
}

static void truth_eval(truth_t *tr, float t)
{
    float rpy[3];
    rpy_profile(t, rpy);
    rpy_to_R(rpy, tr->R_wb);
    gyro_at(t, tr->gyro);
    vel_profile(t, tr->vel);

    const float h = 1.0e-3f;
    float va[3], vb[3];
    vel_profile(t - h, va);
    vel_profile(t + h, vb);
    for (int i = 0; i < 3; i++) tr->acc[i] = (vb[i] - va[i]) / (2.0f * h);

    tr->stationary = (motion_gate(t) < 1.0e-3f);
    tr->t = t;
}

static void truth_init(truth_t *tr)
{
    memset(tr, 0, sizeof(*tr));

    /* Апарат стартує на висоті 1.5 м над поверхнею (вісь Z вниз). */
    tr->pos[2] = -1.5f;

    /* Залишковий зсув нуля акселерометра після заводського калібрування —
       саме те, що фільтр має знайти сам. Гіроскоп теж не ідеальний, але
       його зсув у стан не входить: він псує орієнтацію, а не швидкість. */
    tr->acc_bias[0] = 0.06f;
    tr->acc_bias[1] = -0.04f;
    tr->acc_bias[2] = 0.03f;

    tr->gyro_bias[0] = 0.002f;
    tr->gyro_bias[1] = -0.001f;
    tr->gyro_bias[2] = 0.0015f;

    truth_eval(tr, 0.0f);
}

static void truth_step(truth_t *tr, float dt)
{
    float v_old[3];
    memcpy(v_old, tr->vel, sizeof(v_old));
    truth_eval(tr, tr->t + dt);
    for (int i = 0; i < 3; i++) tr->pos[i] += 0.5f * (v_old[i] + tr->vel[i]) * dt;
}

static float truth_height(const truth_t *tr)
{
    return -tr->pos[2];
}

/* ── Давачі ──────────────────────────────────────────────────────────────
   Кожна модель — точна обернена дія до того, що робить відповідний модуль
   навігації: IMU повертає прискорення в систему тіла й додає гравітацію
   назад, потік перетворює швидкість на пікселі, доклавши обертання. */

static void imu_read(truth_t *tr, float a_meas[3], float gyro_meas[3])
{
    float a_world[3], RT[3][3];
    for (int i = 0; i < 3; i++) a_world[i] = tr->acc[i];
    a_world[2] -= EKF_GRAVITY_MSS;      /* акселерометр міряє питому силу */

    transpose(RT, tr->R_wb);
    ekf_rotate(a_meas, RT, a_world);

    for (int i = 0; i < 3; i++) {
        a_meas[i] += tr->acc_bias[i] + ACC_NOISE * rng_gauss();
        gyro_meas[i] = tr->gyro[i] + tr->gyro_bias[i] + GYRO_NOISE * rng_gauss();
    }
}

static void flow_frame(truth_t *tr, float dt_frame, int16_t *dpx, int16_t *dpy, uint8_t *squal)
{
    tr->flow_frames++;

    const float h = truth_height(tr);
    const float d = (h > 0.05f) ? h : 0.05f;

    float RT[3][3], v_body[3];
    transpose(RT, tr->R_wb);
    ekf_rotate(v_body, RT, tr->vel);

    /* Обернена деротація: до поступальної складової додаємо ту, що її
       створює обертання апарата. Модуль потоку робитиме зворотне. */
    const float w_x = v_body[0] / d + tr->gyro[1];
    const float w_y = v_body[1] / d - tr->gyro[0];

    float px = w_x * dt_frame / RAD_PER_PIXEL + FLOW_NOISE * rng_gauss();
    float py = w_y * dt_frame / RAD_PER_PIXEL + FLOW_NOISE * rng_gauss();

    uint8_t q = 120;

    /* Кожен 137-й кадр — поверхня без текстури (свіжий асфальт, вода).
       Сенсор чесно попереджає низьким SQUAL: кадр має бути відкинутий ще
       до фільтра. */
    if ((tr->flow_frames % 137u) == 0u) q = 12;

    /* Кожен 331-й — відблиск або змаз: якість висока, числа брехливі.
       Ось цей випадок ловить уже тільки строб Махаланобіса. */
    if ((tr->flow_frames % 331u) == 0u) {
        px *= 6.0f;
        py *= -4.0f;
    }

    *dpx = (int16_t)lrintf(px);
    *dpy = (int16_t)lrintf(py);
    *squal = q;
}

static float range_read(truth_t *tr)
{
    tr->range_reads++;

    const float tilt_cos = tr->R_wb[2][2];
    float range = truth_height(tr) / ((tilt_cos > 0.1f) ? tilt_cos : 0.1f);
    range += RANGE_NOISE * rng_gauss();

    /* Кожне 211-те читання — промінь спіймав кущ: дальність різко менша. */
    if ((tr->range_reads % 211u) == 0u) range *= 0.45f;
    return range;
}

/* ── Детектор нерухомості ────────────────────────────────────────────────
   Умова стоянки — і модуль питомої сили близький до g, і кутова швидкість
   мала, і так протягом усього вікна. Одного відліку тут мало: у момент
   зміни напрямку руху прискорення теж проходить через g, а вікно в 128 мс
   такий проліт відсіює. */

#define STILL_WIN 64

typedef struct {
    float acc_mag[STILL_WIN];
    float gyro_mag[STILL_WIN];
    unsigned idx, count;
} still_t;

static bool still_update(still_t *s, const float a_body[3], const float gyro[3])
{
    const float am = sqrtf(a_body[0] * a_body[0] + a_body[1] * a_body[1] + a_body[2] * a_body[2]);
    const float gm = sqrtf(gyro[0] * gyro[0] + gyro[1] * gyro[1] + gyro[2] * gyro[2]);

    s->acc_mag[s->idx] = am;
    s->gyro_mag[s->idx] = gm;
    s->idx = (s->idx + 1u) % STILL_WIN;
    if (s->count < STILL_WIN) s->count++;

    if (s->count < STILL_WIN) return false;

    for (unsigned i = 0; i < STILL_WIN; i++) {
        if (fabsf(s->acc_mag[i] - EKF_GRAVITY_MSS) > 0.30f) return false;
        if (s->gyro_mag[i] > 0.05f) return false;
    }
    return true;
}

/* ── Компенсація затримки вимірювань ─────────────────────────────────────
   Кадр потоку описує момент, який уже минув: поки кадр знято, приїхало по
   SPI й оброблено, апарат устиг змінити швидкість. Влити таке вимірювання
   в поточний стан означає систематично тягнути оцінку назад.

   Дешевий і чесний спосіб — перенести саме ВИМІРЮВАННЯ вперед: фільтр
   знає, на скільки він змінив швидкість і координату відтоді, і рівно ці
   прирости треба додати до запізнілого числа. Кільцевий буфер приростів
   на 128 мс покриває будь-яку реальну затримку конвеєра давачів.

   PX4 і ArduPilot роблять строгіший варіант тієї самої думки: там у
   буфері лежать цілі стани фільтра, корекція застосовується заднім числом
   до історичного зрізу, а вперед переінтегровується весь буфер. Це точніше
   на різких маневрах і дорожче за пам'яттю та часом. */

#define DELTA_WIN 64

typedef struct {
    uint32_t t_us[DELTA_WIN];
    float dv[DELTA_WIN][3];
    float dp[DELTA_WIN][3];
    unsigned idx, count;
} deltas_t;

static void deltas_push(deltas_t *d, uint32_t t_us, const float dv[3], const float dp[3])
{
    d->t_us[d->idx] = t_us;
    for (int i = 0; i < 3; i++) {
        d->dv[d->idx][i] = dv[i];
        d->dp[d->idx][i] = dp[i];
    }
    d->idx = (d->idx + 1u) % DELTA_WIN;
    if (d->count < DELTA_WIN) d->count++;
}

/* Сумарні прирости від моменту t_meas і дотепер. */
static void deltas_since(const deltas_t *d, uint32_t t_meas_us, float dv[3], float dp[3])
{
    for (int i = 0; i < 3; i++) dv[i] = dp[i] = 0.0f;

    for (unsigned k = 0; k < d->count; k++) {
        /* Ідемо від найновішого назад, поки відліки молодші за вимірювання. */
        unsigned pos = (d->idx + DELTA_WIN - 1u - k) % DELTA_WIN;
        if (d->t_us[pos] <= t_meas_us) break;
        for (int i = 0; i < 3; i++) {
            dv[i] += d->dv[pos][i];
            dp[i] += d->dp[pos][i];
        }
    }
}

/* ── Публікація стану для контуру керування ──────────────────────────────
   Оцінку читає задача PID, а пише її задача IMU з вищим пріоритетом і
   правом перервати читача посеред структури. Мьютекс тут заборонений:
   високопріоритетна задача не має права чекати на низькопріоритетну.

   Класичний вихід — seqlock. Писар піднімає лічильник до непарного, кладе
   дані, піднімає до парного. Читач бачить непарний лічильник або його
   зміну під час читання — і просто читає ще раз. Писар не блокується
   ніколи, читач у найгіршому разі повторює кілька тактів. */

typedef struct {
    uint32_t t_us;
    float pos[3];
    float vel[3];
    float sigma_pos;
} nav_state_t;

typedef struct {
    _Atomic uint32_t seq;
    nav_state_t data;
} nav_pub_t;

static void pub_write(nav_pub_t *pub, const nav_state_t *s)
{
    const uint32_t seq = atomic_load_explicit(&pub->seq, memory_order_relaxed);
    atomic_store_explicit(&pub->seq, seq + 1u, memory_order_relaxed);  /* непарний */
    atomic_thread_fence(memory_order_release);

    pub->data = *s;

    atomic_thread_fence(memory_order_release);
    atomic_store_explicit(&pub->seq, seq + 2u, memory_order_relaxed);  /* парний */
}

static bool pub_read(const nav_pub_t *pub, nav_state_t *out)
{
    for (int attempt = 0; attempt < 4; attempt++) {
        const uint32_t before = atomic_load_explicit(&pub->seq, memory_order_relaxed);
        if (before & 1u) continue;                  /* писар саме в структурі */
        atomic_thread_fence(memory_order_acquire);

        *out = pub->data;

        atomic_thread_fence(memory_order_acquire);
        if (atomic_load_explicit(&pub->seq, memory_order_relaxed) == before) return true;
    }
    return false;   /* нас переривали чотири рази поспіль — беремо старий знімок */
}

/* ── Черга «сенсор → навігація» ──────────────────────────────────────────
   Вимірювання не з'являється в обробнику миттєво. Затримку відтворюємо
   явно — інакше половина роботи компенсації лишилася б непоказаною. */

#define PEND_N 8

typedef struct {
    bool used;
    bool is_flow;
    uint32_t deliver_us;        /* коли вимірювання доїде до задачі */
    uint32_t t_us;              /* момент, ЯКИЙ воно описує */
    int16_t dpx, dpy;
    uint8_t squal;
    float dt_frame;
    float gyro[3];
    float R_wb[3][3];
    float range_raw;
} pending_t;

static void pend_put(pending_t q[PEND_N], const pending_t *item)
{
    for (int i = 0; i < PEND_N; i++) {
        if (!q[i].used) {
            q[i] = *item;
            q[i].used = true;
            return;
        }
    }
    /* Черга переповнена — це вже збій розкладу задач, а не норма.
       Найстаріше вимірювання втрачаємо свідомо: краще пропустити кадр,
       ніж накопичувати ще довшу затримку. */
    unsigned oldest = 0;
    for (int i = 1; i < PEND_N; i++) {
        if (q[i].deliver_us < q[oldest].deliver_us) oldest = (unsigned)i;
    }
    q[oldest] = *item;
    q[oldest].used = true;
}

int main(void)
{
    truth_t truth;
    ekf_dr_t ekf;                /* повний фільтр із корекціями */
    ekf_dr_t inertial;           /* та сама механіка, але без жодної корекції */
    flow_cfg_t flow;
    still_t still = {0};
    deltas_t deltas = {0};
    pending_t pend[PEND_N] = {0};
    nav_pub_t pub;

    memset(&pub.data, 0, sizeof(pub.data));
    atomic_init(&pub.seq, 0u);

    truth_init(&truth);
    ekf_dr_init(&ekf);
    ekf_dr_init(&inertial);
    flow_init(&flow);

    /* Обидва фільтри стартують із правильної початкової позиції: далі
       розходження — це вже тільки робота давачів. */
    ekf.x[EKF_PZ] = truth.pos[2];
    inertial.x[EKF_PZ] = truth.pos[2];

    uint32_t n_flow_fused = 0, n_flow_dropped = 0, n_zupt = 0, n_range_fused = 0;
    uint32_t t_us = 0;

    printf("  t,с | висота |  похибка позиції, м  | оцінка зсуву акс., м/с²  | σ_pos\n");
    printf("      |    м   |  фільтр    інерція   |   x       y       z      |   м\n");
    printf("------+--------+----------------------+--------------------------+-------\n");

    for (uint32_t step = 0; step < STEPS; step++, t_us += DT_US) {
        truth_step(&truth, DT_S);

        /* ── Задача IMU, 500 Гц, найвищий пріоритет ── */
        float a_body[3], gyro[3];
        imu_read(&truth, a_body, gyro);

        float v_before[3], p_before[3], v_after[3], p_after[3];
        ekf_dr_get_state(&ekf, p_before, v_before, NULL);

        if (!ekf_dr_predict(&ekf, a_body, truth.R_wb, DT_S)) {
            /* На апараті сюди потрапляють збійні відліки IMU; крок
               пропущено, наступний відлік просто прийде з більшим dt. */
            continue;
        }
        ekf_dr_predict(&inertial, a_body, truth.R_wb, DT_S);

        ekf_dr_get_state(&ekf, p_after, v_after, NULL);
        float dv[3], dp[3];
        for (int i = 0; i < 3; i++) {
            dv[i] = v_after[i] - v_before[i];
            dp[i] = p_after[i] - p_before[i];
        }
        deltas_push(&deltas, t_us, dv, dp);

        /* Детектор нерухомості й ZUPT. Строб усередині фільтра лишає
           за собою останнє слово, якщо детектор помилився. */
        const bool stationary = still_update(&still, a_body, gyro);
        if (stationary && (step % 25u) == 0u) {      /* 20 Гц вистачає */
            if (ekf_dr_update_zupt(&ekf, 0.0025f) == EKF_FUSED) n_zupt++;
        }

        /* ── Задача давачів: кадри лягають у чергу із затримкою ── */
        if ((step % FLOW_EVERY) == 0u) {
            pending_t item = {0};
            item.is_flow = true;
            item.t_us = t_us;
            item.deliver_us = t_us + FLOW_LATENCY_US;
            item.dt_frame = DT_S * (float)FLOW_EVERY;
            flow_frame(&truth, item.dt_frame, &item.dpx, &item.dpy, &item.squal);
            memcpy(item.gyro, gyro, sizeof(item.gyro));
            memcpy(item.R_wb, truth.R_wb, sizeof(item.R_wb));
            item.range_raw = range_read(&truth);
            pend_put(pend, &item);
        }
        if ((step % RANGE_EVERY) == 0u) {
            pending_t item = {0};
            item.is_flow = false;
            item.t_us = t_us;
            item.deliver_us = t_us + RANGE_LATENCY_US;
            memcpy(item.R_wb, truth.R_wb, sizeof(item.R_wb));
            item.range_raw = range_read(&truth);
            pend_put(pend, &item);
        }

        /* ── Те, що вже доїхало, зливаємо ── */
        for (int i = 0; i < PEND_N; i++) {
            if (!pend[i].used || pend[i].deliver_us > t_us) continue;
            pending_t m = pend[i];
            pend[i].used = false;

            float back_dv[3], back_dp[3];
            deltas_since(&deltas, m.t_us, back_dv, back_dp);

            if (m.is_flow) {
                flow_meas_t fm;
                if (!flow_measure(&flow, m.dpx, m.dpy, m.squal, m.dt_frame,
                                  m.gyro, m.R_wb, m.range_raw, &fm)) {
                    n_flow_dropped++;
                    continue;
                }

                /* Вимірювання описує швидкість у минулому — переносимо його
                   вперед на той приріст, який фільтр устиг накрутити. */
                const float vx = fm.vx_world + back_dv[0];
                const float vy = fm.vy_world + back_dv[1];

                /* Строб 4.0 — це 2σ за χ² з одним ступенем вільності. */
                if (ekf_dr_update_velocity2d(&ekf, vx, vy, fm.r_cov, 4.0f) == EKF_FUSED) {
                    n_flow_fused++;
                } else {
                    n_flow_dropped++;
                }
            } else {
                const float tilt_cos = m.R_wb[2][2];
                if (!(tilt_cos > 0.70f)) continue;

                /* Дальність уздовж променя × косинус нахилу = висота;
                   у NED вона від'ємна (вісь Z вниз). */
                const float pz = -(m.range_raw * tilt_cos) + back_dp[2];
                const float r_cov = 0.0004f + 0.01f * m.range_raw * m.range_raw;

                if (ekf_dr_update_altitude(&ekf, pz, r_cov, 4.0f) == EKF_FUSED) {
                    n_range_fused++;
                }
            }
        }

        /* Свіжу оцінку віддаємо контуру керування. На апараті це кінець
           обробника переривання IMU: далі стан читає задача PID. */
        {
            nav_state_t snap;
            snap.t_us = t_us;
            ekf_dr_get_state(&ekf, snap.pos, snap.vel, NULL);
            snap.sigma_pos = ekf_dr_pos_sigma(&ekf, 0);
            pub_write(&pub, &snap);
        }

        /* ── Звіт: читаємо так само, як його читав би контур керування ── */
        if ((step % REPORT_EVERY) == 0u) {
            nav_state_t snap;
            float bias[3], pos_i[3];
            if (!pub_read(&pub, &snap)) continue;

            ekf_dr_get_state(&ekf, NULL, NULL, bias);
            ekf_dr_get_state(&inertial, pos_i, NULL, NULL);

            const float *pos = snap.pos;
            float err = 0.0f, err_i = 0.0f;
            for (int i = 0; i < 3; i++) {
                const float d1 = pos[i] - truth.pos[i];
                const float d2 = pos_i[i] - truth.pos[i];
                err += d1 * d1;
                err_i += d2 * d2;
            }

            printf("%5.1f | %6.2f | %8.2f %10.2f | %7.3f %7.3f %7.3f | %5.2f%s\n",
                   (double)truth.t, (double)truth_height(&truth),
                   (double)sqrtf(err), (double)sqrtf(err_i),
                   (double)bias[0], (double)bias[1], (double)bias[2],
                   (double)snap.sigma_pos,
                   stationary ? "  [стоїмо]" : "");
        }
    }

    printf("\nІстинний зсув акселерометра: %.3f %.3f %.3f м/с²\n",
           (double)truth.acc_bias[0], (double)truth.acc_bias[1], (double)truth.acc_bias[2]);
    printf("Кадрів потоку злито %u, відкинуто %u (якість %u, змаз %u, дальність %u, нахил %u)\n",
           n_flow_fused, n_flow_dropped, flow.n_quality, flow.n_rate, flow.n_range, flow.n_tilt);
    printf("Далекомір злито %u, ZUPT %u, строб фільтра відкинув %u, чисельних відмов %u\n",
           n_range_fused, n_zupt, ekf.n_gated, ekf.n_numeric);
    printf("Коваріацію рятувала гігієна %u разів\n", ekf.n_reset);

    return 0;
}
