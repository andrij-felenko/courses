#include <stddef.h>
#include <stdint.h>

// Вільний слот несе всередині тільки посилання на наступний вільний.
// Тому розмір слота мусить бути не меншим за sizeof(Slot).
typedef struct Slot {
    struct Slot *next;
} Slot;

typedef struct {
    Slot    *free_head;   // вершина стека вільних слотів
    uint8_t *arena;       // початок суцільної арени
    size_t   slot_size;   // розмір одного слота, байтів
    size_t   count;       // N — скільки слотів усього
} Pool;

// Нарізати арену на N слотів і зшити всі у вільний список.
void pool_init(Pool *p, void *arena, size_t slot_size, size_t count) {
    p->arena     = (uint8_t *)arena;
    p->slot_size = slot_size;
    p->count     = count;
    p->free_head = NULL;
    // зшиваємо з кінця, щоб на виході голова вказувала на слот 0
    for (size_t i = count; i-- > 0; ) {
        Slot *slot   = (Slot *)(p->arena + i * slot_size);
        slot->next   = p->free_head;   // next лежить у тілі вільного слота
        p->free_head = slot;
    }
}

// Виділити слот = зняти верхній елемент стека вільних. O(1).
void *pool_alloc(Pool *p) {
    if (p->free_head == NULL)          // слоти скінчились — чесна відмова
        return NULL;
    Slot *block  = p->free_head;
    p->free_head = block->next;        // голова з'їжджає на наступний вільний
    return block;                      // тіло слота тепер віддане даним
}

// Звільнити слот = покласти назад на вершину стека. O(1).
void pool_free(Pool *p, void *ptr) {
    if (ptr == NULL)
        return;
    Slot *slot   = (Slot *)ptr;
    slot->next   = p->free_head;       // старий верх стає наступним
    p->free_head = slot;               // а звільнений слот — новим верхом
}
