#include <stdint.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

#define THERMAL_WIDTH   160
#define THERMAL_HEIGHT  120
#define THERMAL_PIXELS  (THERMAL_WIDTH * THERMAL_HEIGHT)
#define HIST_BINS       16384
#define PLATEAU_LIMIT   20

typedef struct {
    uint8_t r;
    uint8_t g;
    uint8_t b;
} Rgb888;

typedef struct {
    float   gain[THERMAL_PIXELS];        /* Калібрувальний коефіцієнт підсилення */
    int32_t offset[THERMAL_PIXELS];      /* Базовий зсув заводського калібрування */
    int32_t shutter[THERMAL_PIXELS];     /* Останній кадр закритої механічної шторки */
    uint8_t bad_mask[THERMAL_PIXELS];    /* 1 = дефектний («битий») піксель, 0 = справний */
    Rgb888  ironbow_lut[256];            /* Таблиця перекодування палітри Ironbow */
    float   global_baseline;             /* Цільовий базовий рівень NUC */
} ThermalPipelineContext;

/* Ініціалізація та генерація таблиці Ironbow LUT */
void thermal_pipeline_init(ThermalPipelineContext *ctx) {
    memset(ctx, 0, sizeof(ThermalPipelineContext));
    ctx->global_baseline = 8192.0f;

    for (int i = 0; i < THERMAL_PIXELS; ++i) {
        ctx->gain[i] = 1.0f;
        ctx->offset[i] = 0;
        ctx->shutter[i] = 0;
        ctx->bad_mask[i] = 0;
    }

    /* Генерація палітри Ironbow (256 кольорів: чорний -> синій -> червоний -> жовтий -> білий) */
    for (int i = 0; i < 256; ++i) {
        float x = (float)i / 255.0f;
        float r, g, b;

        if (x < 0.25f) {
            float t = x / 0.25f;
            r = 0.0f;
            g = 0.0f;
            b = t;
        } else if (x < 0.50f) {
            float t = (x - 0.25f) / 0.25f;
            r = t;
            g = 0.0f;
            b = 1.0f - 0.5f * t;
        } else if (x < 0.75f) {
            float t = (x - 0.50f) / 0.25f;
            r = 1.0f;
            g = t;
            b = 0.5f * (1.0f - t);
        } else {
            float t = (x - 0.75f) / 0.25f;
            r = 1.0f;
            g = 1.0f;
            b = t;
        }

        ctx->ironbow_lut[i].r = (uint8_t)(fminf(fmaxf(r * 255.0f, 0.0f), 255.0f));
        ctx->ironbow_lut[i].g = (uint8_t)(fminf(fmaxf(g * 255.0f, 0.0f), 255.0f));
        ctx->ironbow_lut[i].b = (uint8_t)(fminf(fmaxf(b * 255.0f, 0.0f), 255.0f));
    }
}

/* Оновлення кадру шторки під час спрацювання механічного калібратора */
void thermal_update_shutter(ThermalPipelineContext *ctx, const uint16_t *raw_shutter_frame) {
    for (int i = 0; i < THERMAL_PIXELS; ++i) {
        ctx->shutter[i] = (int32_t)raw_shutter_frame[i];
    }
}

/* Етап 1: NUC-корекція підсилення та зміщення шторки */
void thermal_apply_nuc(const ThermalPipelineContext *ctx, const uint16_t *raw_in, float *nuc_out) {
    for (int i = 0; i < THERMAL_PIXELS; ++i) {
        /* Віднімання ізотермічного зміщення шторки та множення на коефіцієнт підсилення */
        float diff = (float)((int32_t)raw_in[i] - ctx->shutter[i]);
        nuc_out[i] = diff * ctx->gain[i] + ctx->global_baseline;
    }
}

/* Етап 2: Заміна дефектних пікселів (BPR) просторовою медіаною/середнім */
void thermal_replace_bad_pixels(const ThermalPipelineContext *ctx, const float *img_in, float *img_out) {
    for (int y = 0; y < THERMAL_HEIGHT; ++y) {
        for (int x = 0; x < THERMAL_WIDTH; ++x) {
            int idx = y * THERMAL_WIDTH + x;

            if (ctx->bad_mask[idx] == 0) {
                img_out[idx] = img_in[idx];
                continue;
            }

            /* Усереднення по валідних 8-сусідах */
            float sum = 0.0f;
            int count = 0;

            for (int dy = -1; dy <= 1; ++dy) {
                int ny = y + dy;
                if (ny < 0 || ny >= THERMAL_HEIGHT) continue;

                for (int dx = -1; dx <= 1; ++dx) {
                    if (dx == 0 && dy == 0) continue;
                    int nx = x + dx;
                    if (nx < 0 || nx >= THERMAL_WIDTH) continue;

                    int nidx = ny * THERMAL_WIDTH + nx;
                    if (ctx->bad_mask[nidx] == 0) {
                        sum += img_in[nidx];
                        count++;
                    }
                }
            }

            img_out[idx] = (count > 0) ? (sum / (float)count) : ctx->global_baseline;
        }
    }
}

/* Етап 3: Plateau Equalization — стиснення 14-біт до 8-біт */
void thermal_plateau_equalization(const float *img_in, uint8_t *img_8bit_out) {
    uint32_t hist[HIST_BINS] = {0};
    uint32_t cdf[HIST_BINS] = {0};

    float min_val = img_in[0];
    float max_val = img_in[0];

    for (int i = 1; i < THERMAL_PIXELS; ++i) {
        if (img_in[i] < min_val) min_val = img_in[i];
        if (img_in[i] > max_val) max_val = img_in[i];
    }

    if (max_val - min_val < 1.0f) {
        memset(img_8bit_out, 128, THERMAL_PIXELS);
        return;
    }

    /* Побудова гістограми вхідних відліків */
    for (int i = 0; i < THERMAL_PIXELS; ++i) {
        int bin = (int)(img_in[i]);
        if (bin < 0) bin = 0;
        if (bin >= HIST_BINS) bin = HIST_BINS - 1;
        hist[bin]++;
    }

    /* Застосування плато-ліміту (Plateau Clipping) для усунення домінування однорідного фону */
    for (int b = 0; b < HIST_BINS; ++b) {
        if (hist[b] > PLATEAU_LIMIT) {
            hist[b] = PLATEAU_LIMIT;
        }
    }

    /* Обчислення кумулятивної функції розподілу (CDF) */
    uint32_t accum = 0;
    for (int b = 0; b < HIST_BINS; ++b) {
        accum += hist[b];
        cdf[b] = accum;
    }

    uint32_t total_clipped = cdf[HIST_BINS - 1];
    if (total_clipped == 0) total_clipped = 1;

    /* Відображення кожного пікселя в діапазон 0..255 */
    for (int i = 0; i < THERMAL_PIXELS; ++i) {
        int bin = (int)(img_in[i]);
        if (bin < 0) bin = 0;
        if (bin >= HIST_BINS) bin = HIST_BINS - 1;

        uint32_t val = (cdf[bin] * 255) / total_clipped;
        img_8bit_out[i] = (uint8_t)(val > 255 ? 255 : val);
    }
}

/* Етап 4: Застосування палітри Ironbow (конвертація 8-біт -> 24-біт RGB888) */
void thermal_apply_colormap(const ThermalPipelineContext *ctx, const uint8_t *img_8bit_in, Rgb888 *rgb_out) {
    for (int i = 0; i < THERMAL_PIXELS; ++i) {
        uint8_t val = img_8bit_in[i];
        rgb_out[i] = ctx->ironbow_lut[val];
    }
}

/* Головна функція обробки одного кадру */
void thermal_process_frame(const ThermalPipelineContext *ctx, const uint16_t *raw_frame, Rgb888 *rgb_output) {
    float nuc_buffer[THERMAL_PIXELS];
    float bpr_buffer[THERMAL_PIXELS];
    uint8_t gray_buffer[THERMAL_PIXELS];

    thermal_apply_nuc(ctx, raw_frame, nuc_buffer);
    thermal_replace_bad_pixels(ctx, nuc_buffer, bpr_buffer);
    thermal_plateau_equalization(bpr_buffer, gray_buffer);
    thermal_apply_colormap(ctx, gray_buffer, rgb_output);
}
