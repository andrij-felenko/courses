/*
 * Цифрова частина вимірювального тракту в зборі: АЦП -> проріджування ->
 * рухоме середнє на період мережі -> експоненційне згладжування ->
 * двоточкове калібрування -> грами.
 *
 * Аналогова частина взята з моделі afe_model, щоб було видно те, чого на живій
 * платі осцилографом не побачиш: як той самий код прошивки поводиться на трьох
 * різних апаратних трактах.
 *
 *   1) стробування 1 кГц без антиаліасингового фільтра;
 *   2) те саме з RC-ланкою 500 Гц — «фільтр же стоїть»;
 *   3) передискретизація 100 кГц з тією ж RC-ланкою і проріджування до 1 кГц.
 *
 * Складання: cc -std=c11 -O2 *.c -lm -o afe
 */

#include "afe_model.h"
#include "calib.h"
#include "filters.h"

#include <inttypes.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>

#define EMA_SHIFT      5      /* alpha = 1/32, стала часу ~32 мс на 1 кГц */
#define SETTLE_MS      300    /* механіка й фільтри після зміни ваги */
#define CALIB_AVG_MS   400    /* усереднення калібрувальної точки */
#define MEASURE_MS     2000
#define REF_WEIGHT_G   10000  /* еталонна гиря 10 кг */
#define TEST_WEIGHT_G  8000   /* вантаж, який потім «зважуємо» */

#define ADC_ZERO_NOMINAL 2048 /* код, який дав би ідеальний тракт при 0 кг */

/* --- Тракт прошивки --- */

typedef struct {
    bool  oversample;
    dec_t dec;
    ma_t  ma;
    ema_t ema;
} chain_t;

typedef struct {
    int32_t raw;  /* що прийшло від АЦП (у режимі 3 — Q4 після проріджування) */
    int32_t ma;   /* після рухомого середнього */
    int32_t ema;  /* після згладжування — це число і йде в калібрування */
} taps_t;

static bool chain_init(chain_t *c, bool oversample)
{
    c->oversample = oversample;
    dec_init(&c->dec);
    ma_init(&c->ma);
    return ema_init(&c->ema, EMA_SHIFT);
}

/*
 * Просуває тракт на одну мілісекунду. Аналогова модель живе своїм життям усі
 * сто кроків по 10 мкс незалежно від того, коли АЦП вирішив стробувати, — саме
 * ця нерівність і породжує аліасинг у режимах 1 і 2.
 *
 * Повертає true, коли відлік можна брати всерйоз (вікно рухомого середнього
 * заповнене); до того на виході середнє неповного вікна.
 */
static bool chain_tick(chain_t *c, afe_t *afe, taps_t *out)
{
    int32_t raw = 0;
    bool have = false;

    for (int i = 0; i < DECIMATION_FACTOR; ++i) {
        int32_t code = (int32_t)afe_step(afe);

        if (c->oversample) {
            int32_t decimated;
            if (dec_push(&c->dec, code, &decimated)) {
                raw = decimated;
                have = true;
            }
        } else if (i == DECIMATION_FACTOR - 1) {
            /* Один строб на мілісекунду; попередні 99 значень напруги
               прошивка не бачила ніколи. */
            raw = code;
            have = true;
        }
    }

    if (!have) {
        return false;
    }

    out->raw = raw;
    out->ma = ma_update(&c->ma, raw);
    out->ema = ema_update(&c->ema, out->ma);
    return ma_ready(&c->ma);
}

/* --- Статистика по вікну вимірювання --- */

typedef struct {
    int32_t min;
    int32_t max;
    int64_t sum;
    int32_t count;
} stat_t;

static void stat_init(stat_t *s)
{
    s->min = INT32_MAX;
    s->max = INT32_MIN;
    s->sum = 0;
    s->count = 0;
}

static void stat_add(stat_t *s, int32_t x)
{
    if (x < s->min) s->min = x;
    if (x > s->max) s->max = x;
    s->sum += x;
    s->count++;
}

static int32_t stat_mean(const stat_t *s)
{
    return s->count ? div_round(s->sum, s->count) : 0;
}

static int32_t stat_peak_to_peak(const stat_t *s)
{
    return s->count ? s->max - s->min : 0;
}

/* --- Процедура калібрування --- */

/*
 * Ставить вагу, дає тракту заспокоїтись і повертає усереднений код.
 * Усереднення тут не косметика: одна точка калібрування, знята по одному
 * відліку, вносить у шкалу весь миттєвий шум тракту назавжди.
 */
static int32_t average_at_load(chain_t *c, afe_t *afe, double load_kg)
{
    taps_t taps;
    stat_t acc;

    afe_set_load(afe, load_kg);
    for (int ms = 0; ms < SETTLE_MS; ++ms) {
        chain_tick(c, afe, &taps);
    }

    stat_init(&acc);
    for (int ms = 0; ms < CALIB_AVG_MS; ++ms) {
        if (chain_tick(c, afe, &taps)) {
            stat_add(&acc, taps.ema);
        }
    }
    return stat_mean(&acc);
}

/* --- Один випробуваний тракт --- */

typedef struct {
    bool    ok;
    int32_t n_zero;         /* код у точці 0 кг */
    int32_t n_span;         /* код у точці 10 кг */
    double  counts_per_kg;  /* нормовано до цілих квантів АЦП */
    int32_t mean_g;         /* середнє показання під вантажем */
    int32_t pp_raw_g;       /* розмах до фільтрів, у грамах */
    int32_t pp_ma_g;        /* після рухомого середнього */
    int32_t pp_ema_g;       /* після згладжування */
} case_result_t;

static int32_t counts_to_grams_span(int32_t counts, double counts_per_kg_chain)
{
    return (int32_t)(counts * 1000.0 / counts_per_kg_chain + 0.5);
}

static case_result_t run_case(bool oversample, bool aaf_on)
{
    case_result_t r = {0};
    afe_t afe;
    chain_t chain;
    calib_t cal;
    taps_t taps;
    stat_t s_raw, s_ma, s_ema;

    afe_init(&afe, 0xC0FFEEu, aaf_on);
    if (!chain_init(&chain, oversample)) {
        return r; /* негодящий коефіцієнт згладжування — далі йти нема куди */
    }

    r.n_zero = average_at_load(&chain, &afe, 0.0);
    r.n_span = average_at_load(&chain, &afe, REF_WEIGHT_G / 1000.0);

    if (!calib_init(&cal, r.n_zero, 0, r.n_span, REF_WEIGHT_G)) {
        return r; /* точки не розійшлися: тракт обірваний або в насиченні */
    }

    const double counts_per_kg_chain = calib_counts_per_kg(&cal);

    afe_set_load(&afe, TEST_WEIGHT_G / 1000.0);
    for (int ms = 0; ms < SETTLE_MS; ++ms) {
        chain_tick(&chain, &afe, &taps);
    }

    stat_init(&s_raw);
    stat_init(&s_ma);
    stat_init(&s_ema);
    for (int ms = 0; ms < MEASURE_MS; ++ms) {
        if (chain_tick(&chain, &afe, &taps)) {
            stat_add(&s_raw, taps.raw);
            stat_add(&s_ma, taps.ma);
            stat_add(&s_ema, taps.ema);
        }
    }

    /* Розмах переводимо в грами тим самим калібруванням: воно однакове для всіх
       трьох точок знімання, бо фільтри мають одиничний коефіцієнт передачі. */
    r.pp_raw_g = counts_to_grams_span(stat_peak_to_peak(&s_raw), counts_per_kg_chain);
    r.pp_ma_g = counts_to_grams_span(stat_peak_to_peak(&s_ma), counts_per_kg_chain);
    r.pp_ema_g = counts_to_grams_span(stat_peak_to_peak(&s_ema), counts_per_kg_chain);
    r.mean_g = calib_to_grams(&cal, stat_mean(&s_ema));

    /* У режимі проріджування коди йдуть у Q4 — зводимо до цілих квантів,
       щоб число можна було порівнювати з розрахунковим. */
    r.counts_per_kg = oversample ? counts_per_kg_chain / DECIMATION_Q
                                 : counts_per_kg_chain;
    r.ok = true;
    return r;
}

static void print_row(const char *title, case_result_t r)
{
    if (!r.ok) {
        printf("| %-38s | %s |\n", title, "калібрування не вдалося");
        return;
    }
    printf("| %-38s | %8" PRId32 " | %8" PRId32 " | %7.2f | %7" PRId32
           " | %8" PRId32 " | %7" PRId32 " | %7" PRId32 " |\n",
           title, r.n_zero, r.n_span, r.counts_per_kg,
           r.mean_g, r.pp_raw_g, r.pp_ma_g, r.pp_ema_g);
}

int main(void)
{
    const double nominal = afe_nominal_counts_per_kg();

    printf("Тракт: міст 2 мВ/В -> AD620 (G = 150.7) -> зміщення 1.65 В -> АЦП 12 біт, Vref = 3.3 В\n");
    printf("Квант АЦП        : %.3f мкВ\n", 3.3 / 4096.0 * 1e6);
    printf("Розрахунково     : %.2f кванта на кілограм (%.1f кванта на межі 20 кг)\n",
           nominal, nominal * 20.0);
    printf("Завади           : 50 Гц залишкова диференційна + ШІМ 980 Гц + тепловий шум\n");
    printf("Прошивка         : рухоме середнє %d відліків (нуль на 50 Гц) + EMA alpha = 1/%d\n\n",
           MA_WINDOW, 1 << EMA_SHIFT);

    case_result_t naked = run_case(false, false);
    case_result_t filtered = run_case(false, true);
    case_result_t oversampled = run_case(true, true);

    printf("Вантаж %.1f кг, вікно спостереження %.1f с; розмах — у грамах\n\n",
           TEST_WEIGHT_G / 1000.0, MEASURE_MS / 1000.0);
    printf("| %-38s | %8s | %8s | %7s | %7s | %8s | %7s | %7s |\n",
           "тракт", "код 0 кг", "код 10кг", "кв./кг", "середнє", "розмах", "після MA", "після EMA");
    printf("|%s|%s|%s|%s|%s|%s|%s|%s|\n",
           "----------------------------------------", "----------", "----------",
           "---------", "---------", "----------", "---------", "---------");
    print_row("1 кГц, без антиаліасингового ФНЧ", naked);
    print_row("1 кГц, RC 500 Гц перед АЦП", filtered);
    print_row("100 кГц + RC 500 Гц, проріджування", oversampled);

    if (!naked.ok || !filtered.ok || !oversampled.ok) {
        fprintf(stderr, "Калібрування не пройшло — далі порівнювати нема чого.\n");
        return 1;
    }

    printf("\nЩо тут видно.\n");
    printf("Завада 980 Гц при стробуванні 1 кГц повертається на |980 - 1000| = 20 Гц.\n");
    printf("Рухоме середнє з вікном %d має нуль на 50 Гц, а не на 20 Гц, і проти\n", MA_WINDOW);
    printf("складеної завади безсиле: %" PRId32 " г розмаху лишаються %" PRId32 " г.\n",
           naked.pp_raw_g, naked.pp_ema_g);
    printf("RC-ланка 500 Гц послаблює 980 Гц лише вдвічі — %" PRId32 " г замість %" PRId32 " г:\n",
           filtered.pp_ema_g, naked.pp_ema_g);
    printf("один полюс на пів октави від Найквіста нічого не вирішує.\n");
    printf("Передискретизація відсуває Найквіста на 50 кГц, і та сама RC-ланка\n");
    printf("разом із проріджувачем лишає %" PRId32 " г розмаху.\n", oversampled.pp_ema_g);

    /* Що показав би той самий тракт без калібрування, за паспортними номіналами. */
    double raw_counts = (double)oversampled.n_zero / DECIMATION_Q;
    double zero_error_kg = (raw_counts - ADC_ZERO_NOMINAL) / nominal;
    double gain_error_pct = (oversampled.counts_per_kg / nominal - 1.0) * 100.0;
    double uncalibrated_kg = (double)TEST_WEIGHT_G / 1000.0
                           * oversampled.counts_per_kg / nominal + zero_error_kg;

    printf("\nЧому двох точок не обійти.\n");
    printf("Порожня платформа дає код %.1f замість розрахункових %d:\n",
           raw_counts, ADC_ZERO_NOMINAL);
    printf("несиметрія моста і зсув середньої точки — це %+.3f кг сталої похибки.\n",
           zero_error_kg);
    printf("Нахил шкали розійшовся з паспортним на %+.2f %% (розкид R_g і Vref).\n",
           gain_error_pct);
    printf("Перерахунок за номіналами дав би %.3f кг замість %.3f кг;\n",
           uncalibrated_kg, TEST_WEIGHT_G / 1000.0);
    printf("двоточкове калібрування показує %.3f кг, не знаючи жодного номіналу.\n",
           oversampled.mean_g / 1000.0);

    return 0;
}
