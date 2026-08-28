#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

// Структура налаштувань генератора сигналів
typedef struct {
    double amp_x;       // Амплітуда X (вольти / пікселі)
    double amp_y;       // Амплітуда Y (вольти / пікселі)
    double freq_x;      // Частота X (Гц)
    double freq_y;      // Частота Y (Гц)
    double phase_deg;   // Зсув фази (градуси)
} lissajous_config_t;

// Структура точки траєкторії
typedef struct {
    double x;
    double y;
} point2d_t;

// Буфер кадру (ASCII-осцилограф)
typedef struct {
    int width;
    int height;
    char *data;
} framebuffer_t;

// Створення буфера кадру
framebuffer_t* fb_create(int w, int h) {
    framebuffer_t *fb = (framebuffer_t*)malloc(sizeof(framebuffer_t));
    if (!fb) return NULL;
    fb->width = w;
    fb->height = h;
    fb->data = (char*)malloc((size_t)(w * h));
    if (!fb->data) {
        free(fb);
        return NULL;
    }
    memset(fb->data, ' ', (size_t)(w * h));
    return fb;
}

// Очищення буфера
void fb_clear(framebuffer_t *fb) {
    if (fb && fb->data) {
        memset(fb->data, ' ', (size_t)(fb->width * fb->height));
    }
}

// Звільнення пам'яті
void fb_free(framebuffer_t *fb) {
    if (fb) {
        free(fb->data);
        free(fb);
    }
}

// Малювання точки в буфері
void fb_draw_point(framebuffer_t *fb, int px, int py, char ch) {
    if (px >= 0 && px < fb->width && py >= 0 && py < fb->height) {
        fb->data[py * fb->width + px] = ch;
    }
}

// Вивід буфера у консоль
void fb_render_console(const framebuffer_t *fb) {
    for (int y = 0; y < fb->height; ++y) {
        for (int x = 0; x < fb->width; ++x) {
            putchar(fb->data[y * fb->width + x]);
        }
        putchar('\n');
    }
}

// Обчислення дискретної траєкторії Ліссажу
int generate_lissajous_points(const lissajous_config_t *cfg, point2d_t *pts, int max_pts, int num_samples) {
    if (!cfg || !pts || num_samples > max_pts) return -1;

    double phase_rad = cfg->phase_deg * M_PI / 180.0;
    double max_f = (cfg->freq_x > cfg->freq_y) ? cfg->freq_x : cfg->freq_y;
    double dt = 1.0 / (max_f * 100.0); // 100 точок на цикл

    for (int i = 0; i < num_samples; ++i) {
        double t = i * dt;
        pts[i].x = cfg->amp_x * sin(2.0 * M_PI * cfg->freq_x * t + phase_rad);
        pts[i].y = cfg->amp_y * sin(2.0 * M_PI * cfg->freq_y * t);
    }

    return num_samples;
}

int main(void) {
    const int W = 61;
    const int H = 25;
    const int SAMPLES = 600;

    framebuffer_t *fb = fb_create(W, H);
    if (!fb) {
        fprintf(stderr, "Помилка виділення пам'яті!\n");
        return 1;
    }

    point2d_t *points = (point2d_t*)malloc(SAMPLES * sizeof(point2d_t));
    if (!points) {
        fb_free(fb);
        return 1;
    }

    // Налаштування: співвідношення частот 1:2 («вісімка»), фаза 45 градусів
    lissajous_config_t config = {
        .amp_x = (double)(W / 2 - 2),
        .amp_y = (double)(H / 2 - 2),
        .freq_x = 100.0,
        .freq_y = 200.0,
        .phase_deg = 45.0
    };

    int count = generate_lissajous_points(&config, points, SAMPLES, SAMPLES);
    int cx = W / 2;
    int cy = H / 2;

    // Малювання осей
    for (int x = 0; x < W; ++x) fb_draw_point(fb, x, cy, '-');
    for (int y = 0; y < H; ++y) fb_draw_point(fb, cx, y, '|');
    fb_draw_point(fb, cx, cy, '+');

    // Проектування точок траєкторії на екран
    for (int i = 0; i < count; ++i) {
        int px = cx + (int)round(points[i].x);
        int py = cy - (int)round(points[i].y);
        fb_draw_point(fb, px, py, '#');
    }

    printf("=== Віртуальний осцилограф (Режим X-Y): fx:fy = 1:2, phase = 45° ===\n\n");
    fb_render_console(fb);

    free(points);
    fb_free(fb);
    return 0;
}
