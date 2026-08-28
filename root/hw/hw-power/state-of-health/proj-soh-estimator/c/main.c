#include <stdbool.h>
#include <stdint.h>

/* Дає решта прошивки: таблиця OCV→SoC і сирий пробіг кулонометра. */
int16_t soc_from_ocv_cpm(int32_t u_mv, int16_t t_c);  /* SoC, сотих відсотка   */
int32_t coulomb_total_mas(void);                      /* пробіг лічильника, мА·с */

/* ── паспорт комірки і межі допуску ──────────────────────────────────────── */
#define Q_RATED_MAS   10800000L  /* 3000 мА·год = 3000×3600 мА·с              */
#define R_NEW_MOHM    30         /* опір нової комірки, зведений до 25 °C     */
#define R_EOL_MOHM    75         /* просадка, якої вже не терпить наша схема  */
#define FLAT_LO_MV    3737       /* пласка ділянка OCV — тут не якорити       */
#define FLAT_HI_MV    3800
#define T_MIN_C       10         /* поза цим вікном ємність не вчимо          */
#define T_MAX_C       40
#define REST_MIN_S    1800       /* спокій перевіряємо не раніше ніж за 30 хв */
#define REST_DVDT_NVS 4000       /* напруга усталилась: |dU/dt| < 4 мкВ/с     */
#define QUIT_MA       150        /* C/20 для 3000 мА·год — межа «спокою»      */
#define SPAN_MIN_CPM  3700       /* найменший розмах якорів: 37.00 %          */
#define DI_MIN_MA     500        /* менший стрибок не дасть точності          */

typedef struct {
    int32_t u_uv;      /* напруга на клемах, мкВ             */
    int32_t i_ma;      /* струм зі знаком: + заряд, − розряд */
    int16_t t_c;       /* температура комірки, °C            */
    int32_t dudt_nvs;  /* модуль дрейфу напруги, нВ/с        */
} meas_t;

typedef struct { int16_t soc_cpm; int32_t q_mark_mas; } anchor_t;

static int32_t  q_full_mas = Q_RATED_MAS;      /* вивчена повна ємність    */
static int32_t  r_q8       = R_NEW_MOHM * 256; /* опір @25 °C, 1/256 мОм   */
static uint32_t learn_w    = 0;                /* накопичена вага вивчення */
static anchor_t prev;
static bool     has_prev   = false;

static int32_t iabs32(int32_t x) { return x < 0 ? -x : x; }
static int32_t clamp32(int32_t x, int32_t lo, int32_t hi)
{
    return x < lo ? lo : (x > hi ? hi : x);
}

/* ── якір: точка, де SoC відомий незалежно від лічильника ────────────────── */
static bool make_anchor(const meas_t *m, uint32_t rest_s, anchor_t *out)
{
    int32_t u_mv = m->u_uv / 1000;
    if (rest_s < REST_MIN_S)                    return false; /* не відлежалась     */
    if (m->dudt_nvs > REST_DVDT_NVS)            return false; /* напруга ще повзе   */
    if (iabs32(m->i_ma) > QUIT_MA)              return false; /* спокій лише на словах */
    if (m->t_c < T_MIN_C || m->t_c > T_MAX_C)   return false; /* холод або спека    */
    if (u_mv > FLAT_LO_MV && u_mv < FLAT_HI_MV) return false; /* пласке плато OCV   */

    out->soc_cpm    = soc_from_ocv_cpm(u_mv, m->t_c);
    out->q_mark_mas = coulomb_total_mas();   /* саме сирий пробіг, не обрізаний */
    return true;
}

/* ── вивчення ємності: витеклий заряд проти пройденої частки шкали ───────── */
static void learn_capacity(const anchor_t *a1, const anchor_t *a2)
{
    int32_t span = (int32_t)a1->soc_cpm - a2->soc_cpm;  /* сотих відсотка */
    int32_t dq   = a1->q_mark_mas - a2->q_mark_mas;     /* мА·с           */
    if (span < 0) { span = -span; dq = -dq; }           /* заряд годиться так само */
    if (span < SPAN_MIN_CPM || dq <= 0) return;         /* замалий розмах — шум    */

    /* dq×10000 переповнює int32 майже в тридцять разів — рахуємо в 64 бітах */
    int32_t q = (int32_t)(((int64_t)dq * 10000) / span);
    if (q < Q_RATED_MAS / 2 || q > Q_RATED_MAS * 12 / 10) return;  /* нісенітниця */

    uint32_t w = (uint32_t)span;                        /* довіра ∝ розмах */
    q_full_mas = (int32_t)(((int64_t)q_full_mas * learn_w + (int64_t)q * w)
                           / (learn_w + w));
    if (learn_w < 20000) learn_w += w;                  /* стеля: далі фільтр глухне */
}

/* ── вхід 1: комірка лежить у спокої (кликати раз на секунду) ────────────── */
void soh_on_rest(const meas_t *m, uint32_t rest_s)
{
    anchor_t a;
    if (!make_anchor(m, rest_s, &a)) return;
    if (has_prev) learn_capacity(&prev, &a);
    prev = a;                                /* свіжий якір заступає старий */
    has_prev = true;
}

/* ── температурна поправка: R(T) = R₂₅·exp(−k·(T−25)), k ≈ 0.028 1/°C ────── */
static const uint16_t rt_gain_q8[16] = {     /* −20…+55 °C кроком 5 °C, 256 = ×1 */
    891, 776, 676, 588, 512, 446, 388, 338, 294, 256, 223, 194, 169, 147, 128, 111
};

static uint16_t rt_gain(int16_t t_c)
{
    int32_t t  = clamp32(t_c, -20, 54) + 20;
    int32_t i  = t / 5, fr = t % 5;
    int32_t a  = rt_gain_q8[i], b = rt_gain_q8[i + 1];
    return (uint16_t)(a + (b - a) * fr / 5);           /* лінійно між вузлами */
}

/* ── вхід 2: навантаження стрибнуло (зрізи до і рівно через 1 с після) ───── */
bool soh_on_load_step(const meas_t *before, const meas_t *after)
{
    int32_t di = iabs32(after->i_ma - before->i_ma);
    int32_t du = before->u_uv - after->u_uv;            /* просідання, мкВ */
    if (di < DI_MIN_MA || du <= 0) return false;

    int32_t r_raw = du / di;                            /* мкВ/мА = мОм напряму */
    int32_t r25   = (int32_t)(((int64_t)r_raw * 256) / rt_gain(after->t_c));

    r_q8 += (r25 * 256 - r_q8) / 8;                     /* фільтр у 1/256 мОм */
    return true;
}

/* ── два обличчя здоров'я і одне число назовні ───────────────────────────── */
int16_t soh_capacity_cpm(void)
{
    return (int16_t)(((int64_t)q_full_mas * 10000) / Q_RATED_MAS);
}

int16_t soh_power_cpm(void)
{
    int32_t r = r_q8 / 256;
    int32_t x = (R_EOL_MOHM - r) * 10000 / (R_EOL_MOHM - R_NEW_MOHM);
    return (int16_t)clamp32(x, 0, 10000);
}

int16_t soh_cpm(void)                        /* обережне: гірше з двох */
{
    int16_t c = soh_capacity_cpm(), p = soh_power_cpm();
    return c < p ? c : p;
}
