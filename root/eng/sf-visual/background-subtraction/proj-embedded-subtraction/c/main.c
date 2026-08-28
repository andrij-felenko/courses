#include <stdint.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#define MAX_BLOBS 32
#define MAX_LABELS 1024

/* Опис знайденого рухомого об'єкта */
typedef struct {
    uint16_t min_x;
    uint16_t min_y;
    uint16_t max_x;
    uint16_t max_y;
    uint32_t area;
    uint16_t cx;
    uint16_t cy;
} Blob;

/* Стан детектора руху */
typedef struct {
    uint16_t width;
    uint16_t height;
    uint8_t threshold;    /* Поріг віднімання (типово 15..30) */
    uint8_t shift_alpha;  /* Зсув для швидкості навчання: alpha = 1 / (1 << shift_alpha) */
    uint32_t min_area;    /* Мінімальна площа об'єкта для фільтрації шуму */
    uint16_t *bg_q8;      /* Буфер фону Q8.8 (W * H * sizeof(uint16_t)) */
    uint8_t *mask_raw;    /* Сира маска різниці (W * H) */
    uint8_t *mask_clean;  /* Очищена маска після морфології (W * H) */
    uint16_t *labels;     /* Буфер міток для CCL (W * H * sizeof(uint16_t)) */
    bool initialized;
} MotionDetector;

/* Ініціалізація структури детектора */
bool detector_init(MotionDetector *d, uint16_t width, uint16_t height,
                   uint8_t threshold, uint8_t shift_alpha, uint32_t min_area) {
    d->width = width;
    d->height = height;
    d->threshold = threshold;
    d->shift_alpha = shift_alpha;
    d->min_area = min_area;
    d->initialized = false;

    size_t num_pixels = (size_t)width * height;
    d->bg_q8 = (uint16_t *)malloc(num_pixels * sizeof(uint16_t));
    d->mask_raw = (uint8_t *)malloc(num_pixels);
    d->mask_clean = (uint8_t *)malloc(num_pixels);
    d->labels = (uint16_t *)malloc(num_pixels * sizeof(uint16_t));

    if (!d->bg_q8 || !d->mask_raw || !d->mask_clean || !d->labels) {
        free(d->bg_q8);
        free(d->mask_raw);
        free(d->mask_clean);
        free(d->labels);
        return false;
    }
    return true;
}

void detector_free(MotionDetector *d) {
    free(d->bg_q8);
    free(d->mask_raw);
    free(d->mask_clean);
    free(d->labels);
}

/* 1. Віднімання фону та селективне оновлення моделі Q8.8 */
void process_background_subtraction(MotionDetector *d, const uint8_t *frame) {
    size_t total = (size_t)d->width * d->height;

    /* Перший кадр ініціалізує модель фону */
    if (!d->initialized) {
        for (size_t i = 0; i < total; ++i) {
            d->bg_q8[i] = (uint16_t)(frame[i] << 8);
            d->mask_raw[i] = 0;
        }
        d->initialized = true;
        return;
    }

    uint8_t t = d->threshold;
    uint8_t s = d->shift_alpha;

    for (size_t i = 0; i < total; ++i) {
        uint8_t cur = frame[i];
        uint8_t bg_val = (uint8_t)(d->bg_q8[i] >> 8);

        /* Модуль різниці */
        int16_t diff = (int16_t)cur - (int16_t)bg_val;
        if (diff < 0) diff = -diff;

        if (diff > t) {
            d->mask_raw[i] = 255; /* Рухомий об'єкт */
            /* Примітка: селективна схема не оновлює фон під активним рухом */
        } else {
            d->mask_raw[i] = 0;   /* Тло */
            /* Оновлення IIR з фіксованою комою: B += (I<<8 - B) >> shift */
            int32_t target = (int32_t)(cur << 8);
            int32_t delta = (target - (int32_t)d->bg_q8[i]) >> s;
            d->bg_q8[i] = (uint16_t)((int32_t)d->bg_q8[i] + delta);
        }
    }
}

/* 2. Швидке морфологічне відкриття 3x3 (Ерозія + Дилатація) */
void apply_morphology(MotionDetector *d) {
    uint16_t w = d->width;
    uint16_t h = d->height;
    uint8_t *src = d->mask_raw;
    uint8_t *dst = d->mask_clean;

    /* Виконуємо ерозію з src у dst */
    for (uint16_t y = 1; y < h - 1; ++y) {
        size_t row = (size_t)y * w;
        for (uint16_t x = 1; x < w - 1; ++x) {
            /* Хрестоподібний структурний елемент 3x3 */
            if (src[row + x] &&
                src[row - w + x] && src[row + w + x] &&
                src[row + x - 1] && src[row + x + 1]) {
                dst[row + x] = 255;
            } else {
                dst[row + x] = 0;
            }
        }
    }

    /* Дилатація з dst назад у src, а фінал записуємо в dst */
    for (uint16_t y = 1; y < h - 1; ++y) {
        size_t row = (size_t)y * w;
        for (uint16_t x = 1; x < w - 1; ++x) {
            if (dst[row + x] ||
                dst[row - w + x] || dst[row + w + x] ||
                dst[row + x - 1] || dst[row + x + 1]) {
                src[row + x] = 255;
            } else {
                src[row + x] = 0;
            }
        }
    }
    /* Копіюємо остаточну чисту маску */
    memcpy(dst, src, (size_t)w * h);
}

/* Допоміжні функції Union-Find для CCL */
static uint16_t uf_find(uint16_t *parent, uint16_t i) {
    while (parent[i] != i) {
        parent[i] = parent[parent[i]];
        i = parent[i];
    }
    return i;
}

static void uf_union(uint16_t *parent, uint16_t i, uint16_t j) {
    uint16_t root_i = uf_find(parent, i);
    uint16_t root_j = uf_find(parent, j);
    if (root_i < root_j) {
        parent[root_j] = root_i;
    } else if (root_i > root_j) {
        parent[root_i] = root_j;
    }
}

/* 3. Двохпрохідне маркування компонент зв'язності (CCL) */
uint8_t extract_blobs(MotionDetector *d, Blob *out_blobs, uint8_t max_blobs) {
    uint16_t w = d->width;
    uint16_t h = d->height;
    uint8_t *mask = d->mask_clean;
    uint16_t *labels = d->labels;

    memset(labels, 0, (size_t)w * h * sizeof(uint16_t));

    uint16_t parent[MAX_LABELS];
    for (uint16_t i = 0; i < MAX_LABELS; ++i) parent[i] = i;

    uint16_t next_label = 1;

    /* Перший прохід: призначення міток та пошук еквівалентностей */
    for (uint16_t y = 1; y < h; ++y) {
        size_t row = (size_t)y * w;
        size_t prev_row = (size_t)(y - 1) * w;
        for (uint16_t x = 1; x < w; ++x) {
            if (!mask[row + x]) continue;

            uint16_t left = labels[row + x - 1];
            uint16_t up = labels[prev_row + x];

            if (left == 0 && up == 0) {
                if (next_label < MAX_LABELS) {
                    labels[row + x] = next_label;
                    next_label++;
                }
            } else if (left != 0 && up == 0) {
                labels[row + x] = left;
            } else if (left == 0 && up != 0) {
                labels[row + x] = up;
            } else {
                labels[row + x] = left;
                if (left != up) {
                    uf_union(parent, left, up);
                }
            }
        }
    }

    /* Акумуляція статистики для кожного кореневого лейбла */
    typedef struct {
        uint16_t min_x, min_y, max_x, max_y;
        uint32_t area;
        uint32_t sum_x, sum_y;
    } LabelStats;

    LabelStats stats[MAX_LABELS];
    for (uint16_t i = 0; i < next_label; ++i) {
        stats[i].min_x = w;
        stats[i].min_y = h;
        stats[i].max_x = 0;
        stats[i].max_y = 0;
        stats[i].area = 0;
        stats[i].sum_x = 0;
        stats[i].sum_y = 0;
    }

    /* Другий прохід: згортання міток та підрахунок метрик */
    for (uint16_t y = 0; y < h; ++y) {
        size_t row = (size_t)y * w;
        for (uint16_t x = 0; x < w; ++x) {
            uint16_t l = labels[row + x];
            if (l == 0) continue;

            uint16_t root = uf_find(parent, l);
            stats[root].area++;
            stats[root].sum_x += x;
            stats[root].sum_y += y;
            if (x < stats[root].min_x) stats[root].min_x = x;
            if (x > stats[root].max_x) stats[root].max_x = x;
            if (y < stats[root].min_y) stats[root].min_y = y;
            if (y > stats[root].max_y) stats[root].max_y = y;
        }
    }

    /* Фільтрація за площею та запис результату */
    uint8_t count = 0;
    for (uint16_t i = 1; i < next_label; ++i) {
        if (parent[i] == i && stats[i].area >= d->min_area) {
            if (count >= max_blobs) break;
            out_blobs[count].min_x = stats[i].min_x;
            out_blobs[count].min_y = stats[i].min_y;
            out_blobs[count].max_x = stats[i].max_x;
            out_blobs[count].max_y = stats[i].max_y;
            out_blobs[count].area = stats[i].area;
            out_blobs[count].cx = (uint16_t)(stats[i].sum_x / stats[i].area);
            out_blobs[count].cy = (uint16_t)(stats[i].sum_y / stats[i].area);
            count++;
        }
    }
    return count;
}
