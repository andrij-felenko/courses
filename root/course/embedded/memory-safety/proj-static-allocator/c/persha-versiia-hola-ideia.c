#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#define POOL_BLOCKS   32          // скільки блоків у пулі
#define POOL_BLOCK_SZ 64          // розмір одного блоку, байтів

// Пам'ять пулу — статична, відведена лінкером ще на збірці.
static uint8_t pool_mem[POOL_BLOCKS][POOL_BLOCK_SZ];

// Голова вільного списку. Поки блок вільний, його перші байти
// тлумачаться як покажчик на наступний вільний блок.
static void *free_list;

void pool_init(void) {
    free_list = NULL;
    // Зшиваємо всі блоки у ланцюжок. Кладемо їх "задом наперед",
    // щоб free_list указував на блок [0] — це не обов'язково, просто
    // зручно для читабельності адрес при налагодженні.
    for (size_t i = POOL_BLOCKS; i-- > 0; ) {
        void *blk = pool_mem[i];
        *(void **)blk = free_list;   // перші байти блоку → поточна голова
        free_list = blk;             // блок стає новою головою
    }
}

void *pool_alloc(void) {
    if (free_list == NULL) {
        return NULL;                 // вільних блоків немає
    }
    void *blk = free_list;           // знімаємо голову
    free_list = *(void **)blk;       // голова → наступний у ланцюжку
    return blk;
}

void pool_free(void *blk) {
    *(void **)blk = free_list;       // блок указує на стару голову
    free_list = blk;                 // блок стає новою головою
}
