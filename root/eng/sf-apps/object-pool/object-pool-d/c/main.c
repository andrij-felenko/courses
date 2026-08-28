// Блоковий пул: усі клітини однакового розміру, зв'язані в список вільних.
// Хитрість: покажчик "наступний вільний" живе В САМІЙ вільній клітині —
// окремої службової пам'яті під облік не треба взагалі.
typedef struct Cell { struct Cell *next; } Cell;

Cell *free_list;                 // голова списку вільних

void *pool_alloc(void) {         // O(1): зняти голову
    Cell *c = free_list;
    if (c) free_list = c->next;
    return c;                     // NULL, якщо пул вичерпано
}

void pool_free(void *p) {        // O(1): повернути в голову
    Cell *c = p;
    c->next = free_list;
    free_list = c;
}
