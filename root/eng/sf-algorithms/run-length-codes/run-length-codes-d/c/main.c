#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

// Повертає значення біта (0 = білий, 1 = чорний)
static inline int get_bit(const uint8_t *row, int x, int width) {
    if (x < 0 || x >= width) return 0;
    return (row[x >> 3] >> (7 - (x & 7))) & 1;
}

// Пошук наступної точки зміни кольору
int find_next_edge(const uint8_t *row, int x, int width) {
    int start_color = get_bit(row, x, width);
    int curr = (x < 0) ? 0 : x + 1;
    while (curr < width) {
        if (get_bit(row, curr, width) != start_color) {
            return curr;
        }
        curr++;
    }
    return width;
}

// Пошук переходу b1 на опорному рядку
int find_b1_edge(const uint8_t *ref, int a0, int width, int a0_color) {
    int target_color = 1 - a0_color;
    int curr = (a0 < 0) ? 0 : a0 + 1;
    while (curr < width) {
        int c = get_bit(ref, curr, width);
        int prev_c = get_bit(ref, curr - 1, width);
        if (c == target_color && c != prev_c) {
            return curr;
        }
        curr++;
    }
    return width;
}

typedef enum {
    MODE_PASS,
    MODE_VERTICAL,
    MODE_HORIZONTAL
} MRMode;

typedef struct {
    MRMode mode;
    int    v_diff;     // для Vertical: -3..+3
    int    run1;       // для Horizontal: довжина першої серії
    int    run2;       // для Horizontal: довжина другої серії
    int    next_a0;    // нове положення опорної точки
    int    next_color; // новий колір опорної точки
} MRStepResult;

MRStepResult mr_classify_step(const uint8_t *ref, const uint8_t *curr,
                              int width, int a0, int a0_color) {
    MRStepResult res;
    int a1 = find_next_edge(curr, a0, width);
    int b1 = find_b1_edge(ref, a0, width, a0_color);
    int b2 = find_next_edge(ref, b1, width);

    if (b2 < a1) {
        res.mode = MODE_PASS;
        res.next_a0 = b2;
        res.next_color = a0_color; // колір зберігається
    } else {
        int diff = a1 - b1;
        if (diff >= -3 && diff <= 3) {
            res.mode = MODE_VERTICAL;
            res.v_diff = diff;
            res.next_a0 = a1;
            res.next_color = 1 - a0_color; // інверсія кольору
        } else {
            int a2 = find_next_edge(curr, a1, width);
            res.mode = MODE_HORIZONTAL;
            res.run1 = a1 - ((a0 < 0) ? 0 : a0);
            res.run2 = a2 - a1;
            res.next_a0 = a2;
            res.next_color = a0_color; // два переходи: колір не змінюється
        }
    }
    return res;
}
