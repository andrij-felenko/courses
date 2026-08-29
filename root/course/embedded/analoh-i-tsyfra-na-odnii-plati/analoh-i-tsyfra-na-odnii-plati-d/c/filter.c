#include "filter.h"

/* Поріг «свій/чужий» = 3·σ, де σ оцінюємо через медіану модулів відхилень:
 * σ ≈ 1.4826·MAD. Множник 3·1.4826 = 4.4478 тримаємо в тисячних, щоб не
 * тягнути на мікроконтролер плаваючу кому. */
#define MAD_SCALE_NUM 4448
#define MAD_SCALE_DEN 1000

/* Підлога порога, у кодах. Коли вхід ідеально тихий, MAD вироджується в
 * нуль — і без підлоги фільтр почав би відкидати геть усе, що не збіглося
 * з медіаною до останнього розряду. */
#define MAD_FLOOR 4

/* Стільки відкинутих відліків поспіль означає, що змінився сам сигнал
 * (тензодавач навантажили), а не прилетіла завада. Тоді вікно скидаємо. */
#define RESYNC_AFTER (FILTER_WINDOW / 2u)

static int32_t abs32(int32_t v)
{
    return (v < 0) ? -v : v;
}

static void sort_asc(int32_t *a, uint8_t n)
{
    /* Вікно з 16 елементів: сортування вставками тут швидше за будь-що
     * складніше й не потребує ні рекурсії, ні пам'яті. */
    for (uint8_t i = 1u; i < n; ++i) {
        int32_t key = a[i];
        uint8_t j = i;
        while (j > 0u && a[j - 1u] > key) {
            a[j] = a[j - 1u];
            --j;
        }
        a[j] = key;
    }
}

static int32_t median_sorted(const int32_t *a, uint8_t n)
{
    if ((n & 1u) != 0u) {
        return a[n / 2u];
    }
    return (int32_t)(((int64_t)a[n / 2u - 1u] + (int64_t)a[n / 2u]) / 2);
}

/* Медіана вікна; у *mad_out — медіана модулів відхилень від неї. */
static int32_t window_median(const robust_filter_t *f, int32_t *mad_out)
{
    int32_t buf[FILTER_WINDOW];

    for (uint8_t i = 0u; i < f->count; ++i) {
        buf[i] = f->window[i];
    }
    sort_asc(buf, f->count);
    int32_t med = median_sorted(buf, f->count);

    for (uint8_t i = 0u; i < f->count; ++i) {
        buf[i] = abs32(f->window[i] - med);
    }
    sort_asc(buf, f->count);
    *mad_out = median_sorted(buf, f->count);

    return med;
}

static int32_t window_mean(const robust_filter_t *f)
{
    int64_t sum = 0;

    for (uint8_t i = 0u; i < f->count; ++i) {
        sum += f->window[i];
    }
    return (int32_t)(sum / (int64_t)f->count);
}

void robust_filter_init(robust_filter_t *f)
{
    for (uint8_t i = 0u; i < FILTER_WINDOW; ++i) {
        f->window[i] = 0;
    }
    f->head = 0u;
    f->count = 0u;
    f->streak = 0u;
    f->accepted = 0u;
    f->rejected = 0u;
}

bool robust_filter_push(robust_filter_t *f, int32_t code, int32_t *out)
{
    if (f->count == FILTER_WINDOW) {
        int32_t mad = 0;
        int32_t med = window_median(f, &mad);

        /* mad сягає мільйонів кодів, тож множення рахуємо в 64 бітах:
         * у int32 воно переповнилося б і поріг став би від'ємним. */
        int64_t threshold = ((int64_t)mad * MAD_SCALE_NUM) / MAD_SCALE_DEN;
        if (threshold < MAD_FLOOR) {
            threshold = MAD_FLOOR;
        }

        if ((int64_t)abs32(code - med) > threshold) {
            f->rejected++;
            f->streak++;

            if (f->streak < RESYNC_AFTER) {
                *out = window_mean(f);
                return true;
            }

            /* Половина вікна поспіль «викиди» — це вже не завада, а новий
             * рівень сигналу. Скидаємо вікно й наповнюємо його заново,
             * інакше фільтр назавжди зачепився б за старе значення. */
            f->head = 0u;
            f->count = 0u;
            f->streak = 0u;
        } else {
            f->streak = 0u;
        }
    }

    f->window[f->head] = code;
    f->head = (uint8_t)((f->head + 1u) % FILTER_WINDOW);
    if (f->count < FILTER_WINDOW) {
        f->count++;
    }
    f->accepted++;

    if (f->count < FILTER_WINDOW) {
        return false;
    }

    *out = window_mean(f);
    return true;
}

int32_t robust_filter_spread(const robust_filter_t *f)
{
    if (f->count == 0u) {
        return 0;
    }

    int32_t lo = f->window[0];
    int32_t hi = f->window[0];

    for (uint8_t i = 1u; i < f->count; ++i) {
        if (f->window[i] < lo) {
            lo = f->window[i];
        }
        if (f->window[i] > hi) {
            hi = f->window[i];
        }
    }
    return hi - lo;
}

uint8_t robust_filter_enob(const robust_filter_t *f)
{
    int32_t spread = robust_filter_spread(f);
    uint8_t noise_bits = 0u;

    while (spread > 0) {
        spread >>= 1;
        noise_bits++;
    }

    return (noise_bits >= 24u) ? 0u : (uint8_t)(24u - noise_bits);
}
