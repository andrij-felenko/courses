#include <stdint.h>

/* Блоковий перемішувач глибини D над словами довжини N.
   Пишемо рядками (слово за словом), у канал віддаємо стовпцями. */
#define D 5      /* глибина: скільки кодових слів у матриці (рядків) */
#define N 8      /* довжина кодового слова в символах (стовпців)     */

void block_interleave(const uint8_t src[D * N], uint8_t dst[D * N]) {
    for (int c = 0; c < N; c++)              /* стовпець за стовпцем — так у канал */
        for (int r = 0; r < D; r++)
            dst[c * D + r] = src[r * N + c]; /* символ рядка r, стовпця c */
}

/* Зворотний — дзеркало: пишемо стовпцями, читаємо рядками. */
void block_deinterleave(const uint8_t src[D * N], uint8_t dst[D * N]) {
    for (int c = 0; c < N; c++)
        for (int r = 0; r < D; r++)
            dst[r * N + c] = src[c * D + r];
}
