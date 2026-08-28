#include <stdint.h>

typedef struct { uint8_t r, g, b; } RGB;

static uint8_t avg2(int a, int b)            { return (uint8_t)((a + b + 1) / 2); }
static uint8_t avg4(int a, int b, int c, int d){ return (uint8_t)((a + b + c + d + 2) / 4); }

// raw[H][W] — сира RGGB-мозаїка; out[H][W] — повний RGB.
// Обробляємо лише ВНУТРІШНІ пікселі 1..H-2 / 1..W-2 (у краю бракує сусідів).
void demosaic_bilinear(int H, int W, const uint8_t raw[H][W], RGB out[H][W]) {
    for (int y = 1; y < H - 1; y++) {
        for (int x = 1; x < W - 1; x++) {
            int up = raw[y-1][x],   dn = raw[y+1][x];
            int lf = raw[y][x-1],   rt = raw[y][x+1];
            int ul = raw[y-1][x-1], ur = raw[y-1][x+1];
            int dl = raw[y+1][x-1], dr = raw[y+1][x+1];
            uint8_t c = raw[y][x];                 // виміряна складова цього пікселя
            int ey = y & 1, ex = x & 1;

            if (ey == 0 && ex == 0) {              // червоний піксель
                out[y][x].r = c;
                out[y][x].g = avg4(up, dn, lf, rt);
                out[y][x].b = avg4(ul, ur, dl, dr);
            } else if (ey == 0 && ex == 1) {       // зелений на R-рядку
                out[y][x].r = avg2(lf, rt);        // червоні — по боках
                out[y][x].g = c;
                out[y][x].b = avg2(up, dn);        // сині — зверху/знизу
            } else if (ey == 1 && ex == 0) {       // зелений на B-рядку
                out[y][x].r = avg2(up, dn);        // червоні — зверху/знизу
                out[y][x].g = c;
                out[y][x].b = avg2(lf, rt);        // сині — по боках
            } else {                               // синій піксель
                out[y][x].r = avg4(ul, ur, dl, dr);
                out[y][x].g = avg4(up, dn, lf, rt);
                out[y][x].b = c;
            }
        }
    }
}
