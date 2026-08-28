#include <stdint.h>
#include <math.h>
#include <stdio.h>

typedef struct { uint8_t r, g, b; } RGB;
typedef void (*demosaic_fn)(int H, int W, const uint8_t raw[H][W], RGB out[H][W]);

// 1) еталон: вертикальні смужки періоду `period` пікселів (жорсткий тест на муар)
static void make_reference(int H, int W, RGB ref[H][W], int period) {
    for (int y = 0; y < H; y++)
        for (int x = 0; x < W; x++) {
            uint8_t v = ((x / period) & 1) ? 230 : 30;   // чорно-білі смуги
            ref[y][x].r = ref[y][x].g = ref[y][x].b = v; // сіра сцена: колір має лишитися сірим!
        }
}

// 2) мозаїка RGGB: у кожній точці лишаємо лише «свій» канал
static void mosaic_rggb(int H, int W, const RGB ref[H][W], uint8_t raw[H][W]) {
    for (int y = 0; y < H; y++)
        for (int x = 0; x < W; x++) {
            int ey = y & 1, ex = x & 1;
            if      (ey == 0 && ex == 0) raw[y][x] = ref[y][x].r;   // червоний піксель
            else if (ey == 1 && ex == 1) raw[y][x] = ref[y][x].b;   // синій
            else                          raw[y][x] = ref[y][x].g;  // зелений
        }
}

// 3) PSNR між демозаїченим і еталоном (усі три канали разом)
static double psnr(int H, int W, const RGB a[H][W], const RGB b[H][W]) {
    double mse = 0.0;
    for (int y = 0; y < H; y++)
        for (int x = 0; x < W; x++) {
            int dr = a[y][x].r - b[y][x].r;
            int dg = a[y][x].g - b[y][x].g;
            int db = a[y][x].b - b[y][x].b;
            mse += dr*dr + dg*dg + db*db;
        }
    mse /= (double)H * W * 3.0;
    if (mse <= 0.0) return 99.0;                 // ідеальний збіг
    return 10.0 * log10(255.0 * 255.0 / mse);
}

// зведення докупи (буфери — статичні, щоб не морочитися з купою у прикладі).
// Розміри окремими макросами HH/WW, щоб не плутати з параметрами H/W вище.
#define HH 64
#define WW 64
static RGB    ref_img[HH][WW], out_img[HH][WW];
static uint8_t raw_img[HH][WW];

double evaluate(demosaic_fn method, int period) {
    make_reference(HH, WW, ref_img, period);
    mosaic_rggb(HH, WW, ref_img, raw_img);
    method(HH, WW, raw_img, out_img);
    return psnr(HH, WW, out_img, ref_img);
}
