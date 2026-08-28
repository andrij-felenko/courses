#include <stdint.h>
#include <stddef.h>

#define POOL_N   16          /* кількість блоків                    */
#define BLOCK_SZ 64          /* розмір кожного блоку, байт          */

static uint8_t pool[POOL_N][BLOCK_SZ];  /* статична пам'ять — НЕ купа */
static void   *freeList;                /* голова списку вільних       */

void pool_init(void)
{
    /* Зшиваємо всі блоки в ланцюг:
       у перших sizeof(void*) байтах кожного вільного блоку
       зберігаємо вказівник на наступний вільний блок.       */
    for (int i = 0; i < POOL_N - 1; i++)
        *(void **)pool[i] = pool[i + 1];   /* pool[i] → pool[i+1] */
    *(void **)pool[POOL_N - 1] = NULL;     /* останній → NULL     */
    freeList = pool[0];                    /* голова = pool[0]    */
}
