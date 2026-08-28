// interlacing_calc.c — обчислення полів та анти-твіттер фільтр на C
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>

#define PAL_LINES 625
#define PAL_FIELD_RATE 50.0f
#define WIDTH 720
#define HEIGHT 576

// Структура для зберігання параметрів розгортки
typedef struct {
    float line_time_us;
    float active_video_us;
    uint32_t total_pixels_per_line;
} VideoTiming;

VideoTiming compute_pal_timing(float pixel_clock_mhz) {
    VideoTiming t;
    float line_rate = (PAL_LINES / 2.0f) * PAL_FIELD_RATE; // 15625 Гц
    t.line_time_us = (1.0f / line_rate) * 1.0e6f;          // 64.0 мкс
    t.active_video_us = 52.0f;                             // 52.0 мкс
    t.total_pixels_per_line = (uint32_t)(pixel_clock_mhz * t.active_video_us);
    return t;
}

// Вертикальний Anti-Twitter фільтр (згладжування яскравості між непарними та парними рядками)
void apply_anti_twitter_filter(uint8_t frame[HEIGHT][WIDTH]) {
    for (int y = 1; y < HEIGHT - 1; y++) {
        for (int x = 0; x < WIDTH; x++) {
            // Зважене усереднення 1:2:1 вздовж вертикалі
            uint16_t val = (uint16_t)frame[y - 1][x] + 
                           2 * (uint16_t)frame[y][x] + 
                           (uint16_t)frame[y + 1][x];
            frame[y][x] = (uint8_t)(val / 4);
        }
    }
}
