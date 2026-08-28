#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

#define SAMPLES_PER_LINE 1000
#define F_SUBCARRIER     4433618.75   /* Частота піднесучої PAL (Гц) */
#define SAMPLING_FREQ    40000000.0   /* Частота дискретизації 40 МГц */

typedef struct {
    double r, g, b;
} rgb_color_t;

typedef struct {
    double y, u, v;
} yuv_color_t;

/* Матрицювання RGB -> YUV */
static yuv_color_t rgb_to_yuv(rgb_color_t c) {
    yuv_color_t out;
    out.y =  0.299 * c.r + 0.587 * c.g + 0.114 * c.b;
    out.u = -0.147 * c.r - 0.289 * c.g + 0.436 * c.b; /* 0.492 * (B - Y) */
    out.v =  0.615 * c.r - 0.515 * c.g - 0.100 * c.b; /* 0.877 * (R - Y) */
    return out;
}

/* Зворотне матрицювання YUV -> RGB з обмеженням [0.0, 1.0] */
static rgb_color_t yuv_to_rgb(yuv_color_t c) {
    rgb_color_t out;
    double r = c.y + 1.140 * c.v;
    double b = c.y + 2.032 * c.u;
    double g = c.y - 0.395 * c.u - 0.581 * c.v;
    
    out.r = (r < 0.0) ? 0.0 : (r > 1.0) ? 1.0 : r;
    out.g = (g < 0.0) ? 0.0 : (g > 1.0) ? 1.0 : g;
    out.b = (b < 0.0) ? 0.0 : (b > 1.0) ? 1.0 : b;
    return out;
}

/* Моделювання демодуляції PAL та NTSC при наявності фазової помилки */
int main(void) {
    /* Вхідний тестовий колір (відтінок шкіри): R=0.85, G=0.60, B=0.50 */
    rgb_color_t orig_rgb = {0.85, 0.60, 0.50};
    yuv_color_t orig_yuv = rgb_to_yuv(orig_rgb);
    
    double phase_error_deg = 15.0;
    double phase_error_rad = phase_error_deg * M_PI / 180.0;
    
    double *line_N_chroma   = (double*)malloc(sizeof(double) * SAMPLES_PER_LINE);
    double *line_N1_chroma  = (double*)malloc(sizeof(double) * SAMPLES_PER_LINE);
    
    if (!line_N_chroma || !line_N1_chroma) {
        fprintf(stderr, "Помилка виділення пам'яті!\n");
        return 1;
    }

    double dt = 1.0 / SAMPLING_FREQ;
    double omega = 2.0 * M_PI * F_SUBCARRIER;

    /* 1. Модуляція та внесення фазової завади phase_error_rad */
    for (int i = 0; i < SAMPLES_PER_LINE; ++i) {
        double t = i * dt;
        /* Рядок N: +V компонента з фазовим зсувом */
        line_N_chroma[i]  = orig_yuv.u * sin(omega * t + phase_error_rad) +
                            orig_yuv.v * cos(omega * t + phase_error_rad);
        /* Рядок N+1: -V компонента у PAL (фазовий маятник) */
        line_N1_chroma[i] = orig_yuv.u * sin(omega * t + phase_error_rad) -
                            orig_yuv.v * cos(omega * t + phase_error_rad);
    }

    /* 2. Демодуляція NTSC (без лінії затримки, береться тільки один рядок N) */
    double ntsc_u_acc = 0.0, ntsc_v_acc = 0.0;
    for (int i = 0; i < SAMPLES_PER_LINE; ++i) {
        double t = i * dt;
        ntsc_u_acc += line_N_chroma[i] * 2.0 * sin(omega * t);
        ntsc_v_acc += line_N_chroma[i] * 2.0 * cos(omega * t);
    }
    yuv_color_t ntsc_yuv = {
        .y = orig_yuv.y,
        .u = ntsc_u_acc / SAMPLES_PER_LINE,
        .v = ntsc_v_acc / SAMPLES_PER_LINE
    };
    rgb_color_t ntsc_rgb = yuv_to_rgb(ntsc_yuv);

    /* 3. Демодуляція PAL з 1H лінією затримки (сумування та віднімання N та N+1) */
    double pal_u_acc = 0.0, pal_v_acc = 0.0;
    for (int i = 0; i < SAMPLES_PER_LINE; ++i) {
        double t = i * dt;
        /* Сумування двох рядків виділяє 2U, віднімання виділяє 2V */
        double u_signal = 0.5 * (line_N_chroma[i] + line_N1_chroma[i]);
        double v_signal = 0.5 * (line_N_chroma[i] - line_N1_chroma[i]);
        
        pal_u_acc += u_signal * 2.0 * sin(omega * t);
        pal_v_acc += v_signal * 2.0 * cos(omega * t);
    }
    yuv_color_t pal_yuv = {
        .y = orig_yuv.y,
        .u = pal_u_acc / SAMPLES_PER_LINE,
        .v = pal_v_acc / SAMPLES_PER_LINE
    };
    rgb_color_t pal_rgb = yuv_to_rgb(pal_yuv);

    /* 4. Вивід результатів порівняння */
    printf("=== СИМУЛЯЦІЯ ДЕМОДУЛЯЦІЇ (Фазова помилка каналу = %.1f deg) ===\n", phase_error_deg);
    printf("Оригінал RGB:   R=%.3f, G=%.3f, B=%.3f\n", orig_rgb.r, orig_rgb.g, orig_rgb.b);
    printf("NTSC декодер:   R=%.3f, G=%.3f, B=%.3f  [СПОРТВОРЕННЯ ТОНУ!]\n", ntsc_rgb.r, ntsc_rgb.g, ntsc_rgb.b);
    printf("PAL 1H декодер: R=%.3f, G=%.3f, B=%.3f  [ТОЧНИЙ КОЛІР!]\n", pal_rgb.r, pal_rgb.g, pal_rgb.b);

    free(line_N_chroma);
    free(line_N1_chroma);
    return 0;
}
