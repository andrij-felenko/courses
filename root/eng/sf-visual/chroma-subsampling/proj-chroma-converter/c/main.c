#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>

// Структура плоского буфера YUV420p
typedef struct {
    int width;
    int height;
    uint8_t *y;
    uint8_t *cb;
    uint8_t *cr;
} Yuv420pFrame;

// Структура повнорозмірного буфера YUV444
typedef struct {
    int width;
    int height;
    uint8_t *y;
    uint8_t *cb;
    uint8_t *cr;
} Yuv444Frame;

// Виділення пам'яті під 4:4:4 кадр
Yuv444Frame* yuv444_create(int width, int height) {
    Yuv444Frame *frame = (Yuv444Frame*)malloc(sizeof(Yuv444Frame));
    if (!frame) return NULL;
    frame->width = width;
    frame->height = height;
    size_t size = (size_t)width * height;
    frame->y = (uint8_t*)malloc(size);
    frame->cb = (uint8_t*)malloc(size);
    frame->cr = (uint8_t*)malloc(size);
    if (!frame->y || !frame->cb || !frame->cr) {
        free(frame->y); free(frame->cb); free(frame->cr); free(frame);
        return NULL;
    }
    return frame;
}

void yuv444_free(Yuv444Frame *frame) {
    if (frame) {
        free(frame->y); free(frame->cb); free(frame->cr); free(frame);
    }
}

// Виділення пам'яті під 4:2:0 planar кадр
Yuv420pFrame* yuv420p_create(int width, int height) {
    Yuv420pFrame *frame = (Yuv420pFrame*)malloc(sizeof(Yuv420pFrame));
    if (!frame) return NULL;
    frame->width = width;
    frame->height = height;
    size_t y_size = (size_t)width * height;
    size_t c_size = (size_t)(width / 2) * (height / 2);
    frame->y = (uint8_t*)malloc(y_size);
    frame->cb = (uint8_t*)malloc(c_size);
    frame->cr = (uint8_t*)malloc(c_size);
    if (!frame->y || !frame->cb || !frame->cr) {
        free(frame->y); free(frame->cb); free(frame->cr); free(frame);
        return NULL;
    }
    return frame;
}

void yuv420p_free(Yuv420pFrame *frame) {
    if (frame) {
        free(frame->y); free(frame->cb); free(frame->cr); free(frame);
    }
}

// Пряме субдискретування 4:4:4 -> 4:2:0 з антиаліасинговим КІХ 2x2
void yuv444_to_420p(const Yuv444Frame *src, Yuv420pFrame *dst) {
    int w = src->width;
    int h = src->height;

    // 1. Канал Y копіюється без змін
    memcpy(dst->y, src->y, (size_t)w * h);

    // 2. Колірні канали фільтруються ФНЧ 2x2 та проріджуються
    int cw = w / 2;
    int ch = h / 2;

    for (int cy = 0; cy < ch; cy++) {
        for (int cx = 0; cx < cw; cx++) {
            int x0 = cx * 2;
            int y0 = cy * 2;
            int x1 = (x0 + 1 < w) ? x0 + 1 : x0;
            int y1 = (y0 + 1 < h) ? y0 + 1 : y0;

            // Зважене усереднення 2x2 для Cb
            uint32_t sum_cb = src->cb[y0 * w + x0] + src->cb[y0 * w + x1] +
                              src->cb[y1 * w + x0] + src->cb[y1 * w + x1];
            dst->cb[cy * cw + cx] = (uint8_t)((sum_cb + 2) >> 2);

            // Зважене усереднення 2x2 для Cr
            uint32_t sum_cr = src->cr[y0 * w + x0] + src->cr[y0 * w + x1] +
                              src->cr[y1 * w + x0] + src->cr[y1 * w + x1];
            dst->cr[cy * cw + cx] = (uint8_t)((sum_cr + 2) >> 2);
        }
    }
}

// Зворотне відновлення 4:2:0 -> 4:4:4 білінійною інтерполяцією
void yuv420p_to_444(const Yuv420pFrame *src, Yuv444Frame *dst) {
    int w = src->width;
    int h = src->height;
    int cw = w / 2;

    // 1. Канал Y копіюється без змін
    memcpy(dst->y, src->y, (size_t)w * h);

    // 2. Білінійна інтерполяція Cb та Cr для кожної точки Y
    for (int y = 0; y < h; y++) {
        for (int x = 0; x < w; x++) {
            // Відносні координати в колірній сітці
            float cx_f = (float)x / 2.0f - 0.25f;
            float cy_f = (float)y / 2.0f - 0.25f;

            int x0 = (int)cx_f;
            int y0 = (int)cy_f;
            if (x0 < 0) x0 = 0;
            if (y0 < 0) y0 = 0;
            int x1 = (x0 + 1 < cw) ? x0 + 1 : x0;
            int y1 = (y0 + 1 < (h / 2)) ? y0 + 1 : y0;

            float fx = cx_f - (float)x0;
            float fy = cy_f - (float)y0;
            if (fx < 0.0f) fx = 0.0f;
            if (fy < 0.0f) fy = 0.0f;

            // Ваги білінійної інтерполяції
            float w00 = (1.0f - fx) * (1.0f - fy);
            float w10 = fx * (1.0f - fy);
            float w01 = (1.0f - fx) * fy;
            float w11 = fx * fy;

            float val_cb = w00 * src->cb[y0 * cw + x0] + w10 * src->cb[y0 * cw + x1] +
                           w01 * src->cb[y1 * cw + x0] + w11 * src->cb[y1 * cw + x1];
            float val_cr = w00 * src->cr[y0 * cw + x0] + w10 * src->cr[y0 * cw + x1] +
                           w01 * src->cr[y1 * cw + x0] + w11 * src->cr[y1 * cw + x1];

            dst->cb[y * w + x] = (uint8_t)(val_cb + 0.5f);
            dst->cr[y * w + x] = (uint8_t)(val_cr + 0.5f);
        }
    }
}
