#include <stdint.h>

#define W 160
#define H 120

// Інтегральне зображення: I[y][x] = сума gray[0..y][0..x].
// uint32_t вистачає: 160·120·255 ≈ 4.9·10⁶ ≪ 4.29·10⁹ (межа uint32).
// Для великих кадрів (понад ~16 Мп·255) брати uint64_t.
static uint32_t I[H][W];

void build_integral(const uint8_t gray[H][W]) {
    for (int y = 0; y < H; y++) {
        uint32_t row_sum = 0;                  // біжуча сума поточного рядка
        for (int x = 0; x < W; x++) {
            row_sum += gray[y][x];
            uint32_t up = (y > 0) ? I[y-1][x] : 0;
            I[y][x] = up + row_sum;            // зверху + накопичене в рядку
        }
    }
}
