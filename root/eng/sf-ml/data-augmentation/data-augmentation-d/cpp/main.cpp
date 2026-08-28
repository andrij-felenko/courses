#include <stdint.h>
#include <stdlib.h>   // rand()

// Обрізати значення до діапазону 0…255 (щоб яскравість не «перелилась»)
static uint8_t clamp8(int v) {
    if (v < 0)   return 0;
    if (v > 255) return 255;
    return (uint8_t)v;
}

// Аугментувати кадр НА МІСЦІ: дзеркало + зсув яскравості + шум.
// img — масив w*h байтів, рядок за рядком.
void augment(uint8_t *img, int w, int h) {
    // 1) з імовірністю 50% — горизонтальне дзеркало (ярлик збережеться)
    if (rand() & 1) {
        for (int y = 0; y < h; ++y) {
            uint8_t *row = img + (size_t)y * w;
            for (int x = 0; x < w / 2; ++x) {
                uint8_t t = row[x];
                row[x] = row[w - 1 - x];   // ліве ↔ праве
                row[w - 1 - x] = t;
            }
        }
    }

    // 2) зсув яскравості на випадкове −40…+40 (імітує різне світло)
    int bright = (rand() % 81) - 40;

    // 3) кожен піксель: зсув яскравості + невеликий шум −10…+10
    for (size_t i = 0; i < (size_t)w * h; ++i) {
        int noise = (rand() % 21) - 10;
        img[i] = clamp8((int)img[i] + bright + noise);
    }
}
