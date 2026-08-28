#include <stdint.h>

#define N_BLOCKS 1024

uint32_t erase_count[N_BLOCKS];   // «пробіг» кожного блока
uint8_t  is_free[N_BLOCKS];       // 1 = блок стертий, готовий приймати запис

// Повертає індекс наймолодшого вільного блока, або -1, якщо вільних нема.
int pick_block_for_write(void)
{
    int best = -1;
    uint32_t best_count = UINT32_MAX;

    for (int b = 0; b < N_BLOCKS; b++) {
        if (is_free[b] && erase_count[b] < best_count) {
            best_count = erase_count[b];
            best = b;                 // цей поки що наймолодший
        }
    }
    return best;                      // сюди й покладемо нові дані
}
