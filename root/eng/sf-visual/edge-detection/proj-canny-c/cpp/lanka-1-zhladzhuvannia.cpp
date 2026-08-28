#include <stdint.h>
#include <math.h>
#include <stdlib.h>

#define IDX(y, x) ((y) * W + (x))

// Ціле ядро Гаусса 5×5 (σ≈1), сума ваг = 159.
static const int GAUSS5[5][5] = {
    {2,  4,  5,  4, 2},
    {4,  9, 12,  9, 4},
    {5, 12, 15, 12, 5},
    {4,  9, 12,  9, 4},
    {2,  4,  5,  4, 2},
};

// Згладити in[H*W] → out[H*W]. Край (рамку 2 пікселі) лишаємо як є (копіюємо).
static void gauss_blur(int H, int W, const uint8_t *in, uint8_t *out) {
    for (int y = 0; y < H; y++) {
        for (int x = 0; x < W; x++) {
            if (y < 2 || y >= H - 2 || x < 2 || x >= W - 2) {
                out[IDX(y, x)] = in[IDX(y, x)];   // край — без обробки
                continue;
            }
            int acc = 0;                          // до 255*159 = 40545 — влазить у int
            for (int ky = -2; ky <= 2; ky++)
                for (int kx = -2; kx <= 2; kx++)
                    acc += GAUSS5[ky + 2][kx + 2] * in[IDX(y + ky, x + kx)];
            out[IDX(y, x)] = (uint8_t)(acc / 159);
        }
    }
}
