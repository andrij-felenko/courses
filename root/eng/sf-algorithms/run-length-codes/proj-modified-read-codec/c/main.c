#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

// Бітовий потік для послідовного запису бітів у вихідний буфер
typedef struct {
    uint8_t *buf;
    size_t   capacity;
    size_t   bit_pos;
} BitWriter;

static void bitwriter_init(BitWriter *bw, uint8_t *buf, size_t capacity) {
    bw->buf = buf;
    bw->capacity = capacity;
    bw->bit_pos = 0;
    if (capacity > 0) {
        memset(buf, 0, capacity);
    }
}

static void bitwriter_put(BitWriter *bw, uint32_t code, uint32_t len) {
    for (int32_t i = (int32_t)len - 1; i >= 0; --i) {
        size_t byte_idx = bw->bit_pos >> 3;
        uint32_t bit_idx = 7 - (bw->bit_pos & 7);
        if (byte_idx < bw->capacity) {
            if ((code >> i) & 1) {
                bw->buf[byte_idx] |= (uint8_t)(1 << bit_idx);
            }
        }
        bw->bit_pos++;
    }
}

// Отримання значення біта в бінарному рядку (0 = білий, 1 = чорний)
static inline int get_pixel(const uint8_t *row, int x, int width) {
    if (x < 0 || x >= width) return 0; // умовні білі поля за межами растра
    return (row[x >> 3] >> (7 - (x & 7))) & 1;
}

// Встановлення значення біта в рядку
static inline void set_pixel(uint8_t *row, int x, int color) {
    if (color) {
        row[x >> 3] |= (uint8_t)(1 << (7 - (x & 7)));
    } else {
        row[x >> 3] &= (uint8_t)~(1 << (7 - (x & 7)));
    }
}

// Пошук наступної зміни кольору починаючи з позиції x
static int find_next_transition(const uint8_t *row, int x, int width) {
    int base_color = get_pixel(row, x, width);
    int curr = (x < 0) ? 0 : x + 1;

    // Швидкий байтовий пропуск однорідних зон
    while ((curr & 7) != 0 && curr < width) {
        if (get_pixel(row, curr, width) != base_color) return curr;
        curr++;
    }
    uint8_t skip_byte = base_color ? 0xFF : 0x00;
    while (curr + 8 <= width && row[curr >> 3] == skip_byte) {
        curr += 8;
    }
    while (curr < width) {
        if (get_pixel(row, curr, width) != base_color) return curr;
        curr++;
    }
    return width;
}

// Пошук b1: перший перехід на опорному рядку протилежного до a0 кольору
static int find_b1(const uint8_t *ref, int a0, int width, int a0_color) {
    int target_color = 1 - a0_color;
    int b1 = (a0 < 0) ? 0 : a0 + 1;
    while (b1 < width) {
        int color = get_pixel(ref, b1, width);
        int prev_color = get_pixel(ref, b1 - 1, width);
        if (color == target_color && color != prev_color) {
            return b1;
        }
        b1++;
    }
    return width;
}

// Пошук b2: наступний перехід на опорному рядку після b1
static int find_b2(const uint8_t *ref, int b1, int width) {
    if (b1 >= width) return width;
    int b1_color = get_pixel(ref, b1, width);
    int b2 = b1 + 1;
    while (b2 < width) {
        if (get_pixel(ref, b2, width) != b1_color) {
            return b2;
        }
        b2++;
    }
    return width;
}

// Таблиця префіксних кодів Гаффмана для білих серій (довжини 0..15)
static const struct { uint16_t code; uint8_t len; } WHITE_MH[16] = {
    {0x0035, 8}, {0x0007, 6}, {0x0007, 4}, {0x0008, 4},
    {0x000B, 4}, {0x000C, 4}, {0x000E, 4}, {0x000F, 4},
    {0x0013, 5}, {0x0014, 5}, {0x0007, 5}, {0x0008, 5},
    {0x0008, 6}, {0x0003, 6}, {0x0034, 6}, {0x0035, 6}
};

static void put_run_length(BitWriter *bw, int run) {
    if (run >= 0 && run < 16) {
        bitwriter_put(bw, WHITE_MH[run].code, WHITE_MH[run].len);
    } else {
        // Запасне кодування фіксованим полем для довгих серій
        bitwriter_put(bw, (uint32_t)run, 12);
    }
}

// Кодування одного рядка за стандартом Modified READ (MR)
size_t mr_encode_line(const uint8_t *ref, const uint8_t *curr, int width,
                      uint8_t *out_buf, size_t out_cap) {
    BitWriter bw;
    bitwriter_init(&bw, out_buf, out_cap);

    int a0 = -1;
    int a0_color = 0; // 0 = білий колір на початку рядка

    while (a0 < width) {
        int a1 = find_next_transition(curr, a0, width);
        int b1 = find_b1(ref, a0, width, a0_color);
        int b2 = find_b2(ref, b1, width);

        if (b2 < a1) {
            // Pass Mode: деталі на опорному рядку зникли
            bitwriter_put(&bw, 0x0001, 4);
            a0 = b2;
        } else {
            int diff = a1 - b1;
            if (diff >= -3 && diff <= 3) {
                // Vertical Mode: зсув контуру від -3 до +3 пікселів
                switch (diff) {
                    case  0: bitwriter_put(&bw, 0x0001, 1); break; // V(0) = '1'
                    case  1: bitwriter_put(&bw, 0x0003, 3); break; // VR(1) = '011'
                    case -1: bitwriter_put(&bw, 0x0002, 3); break; // VL(1) = '010'
                    case  2: bitwriter_put(&bw, 0x0003, 6); break; // VR(2) = '000011'
                    case -2: bitwriter_put(&bw, 0x0002, 6); break; // VL(2) = '000010'
                    case  3: bitwriter_put(&bw, 0x0003, 7); break; // VR(3) = '0000011'
                    case -3: bitwriter_put(&bw, 0x0002, 7); break; // VL(3) = '0000010'
                }
                a0 = a1;
                a0_color = 1 - a0_color; // інверсія кольору опорного переходу
            } else {
                // Horizontal Mode: кодування двох послідовних довжин серій
                int a2 = find_next_transition(curr, a1, width);
                bitwriter_put(&bw, 0x0001, 3); // Префікс '001'
                put_run_length(&bw, a1 - ((a0 < 0) ? 0 : a0));
                put_run_length(&bw, a2 - a1);
                a0 = a2;
            }
        }
    }
    return (bw.bit_pos + 7) >> 3;
}
