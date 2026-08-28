// deinterlacer.c — адаптивний деінтерлейсер на C
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdint.h>
#include <stdbool.h>

#define WIDTH 640
#define HEIGHT 480
#define THRESHOLD 15

typedef struct {
    uint8_t data[HEIGHT][WIDTH];
} Field;

typedef struct {
    uint8_t data[HEIGHT][WIDTH];
} Frame;

// Адаптивний деінтерлейсер: обробляє поточне поле, попереднє поле тієї ж парності
// та будує вихідний прогресивний кадр.
void process_deinterlace_field(const Field *curr_field, const Field *prev_same_field,
                               bool is_odd_field, Frame *out_frame) {
    for (int y = 0; y < HEIGHT; y++) {
        // Визначаємо, чи належить поточний рядок кадру даному полю
        bool line_belongs_to_field = ((y % 2 == 0) == is_odd_field);

        for (int x = 0; x < WIDTH; x++) {
            if (line_belongs_to_field) {
                // Рядок наявний у поточному полі — копіюємо без змін
                out_frame->data[y][x] = curr_field->data[y][x];
            } else {
                // Відсутній рядок: перевіряємо детектор руху
                uint8_t p_curr = curr_field->data[y][x];
                uint8_t p_prev = prev_same_field->data[y][x];
                int diff = abs((int)p_curr - (int)p_prev);

                if (diff < THRESHOLD) {
                    // Статична зона: Weave (беремо значення з попереднього кадру)
                    out_frame->data[y][x] = p_curr;
                } else {
                    // Рухома зона: Bob (просторова інтерполяція між верхнім і нижнім рядками)
                    int top_y = (y > 0) ? (y - 1) : 0;
                    int bot_y = (y < HEIGHT - 1) ? (y + 1) : (HEIGHT - 1);
                    uint16_t avg = ((uint16_t)curr_field->data[top_y][x] +
                                    (uint16_t)curr_field->data[bot_y][x]) / 2;
                    out_frame->data[y][x] = (uint8_t)avg;
                }
            }
        }
    }
}
