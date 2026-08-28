#include <stddef.h>
#include <stdint.h>

typedef struct Block {
    size_t        size;   // розмір ТІЛА блока, байтів (без заголовка й footer)
    int           free;   // 1 — вільний, 0 — зайнятий
    struct Block *next;   // наступний вільний блок (дійсний лише коли free)
} Block;

#define HDR    sizeof(Block)     // заголовок перед тілом
#define FTR    sizeof(size_t)    // граничний тег (footer) у кінці блока
#define THRESH 16                // менший хвіст не відрізаємо
#define ALIGN  8                 // вирівнювання тіла

static uint8_t *heap_start, *heap_end;   // межі арени
static Block   *free_list;               // голова списку вільних

static size_t align_up(size_t n) {
    return (n + (ALIGN - 1)) & ~(size_t)(ALIGN - 1);
}
static void  *body_of(Block *b)  { return (uint8_t *)b + HDR; }
static Block *block_of(void *p)  { return (Block *)((uint8_t *)p - HDR); }

// Записати граничний тег — дублікат розміру тіла в кінці блока.
static void set_footer(Block *b) {
    *(size_t *)((uint8_t *)b + HDR + b->size) = b->size;
}
// Фізичний сусід праворуч (за адресою); NULL, якщо блок останній.
static Block *next_phys(Block *b) {
    uint8_t *n = (uint8_t *)b + HDR + b->size + FTR;
    return n < heap_end ? (Block *)n : NULL;
}
// Фізичний сусід ліворуч — через його footer; NULL, якщо блок перший.
static Block *prev_phys(Block *b) {
    if ((uint8_t *)b <= heap_start) return NULL;
    size_t psize = *(size_t *)((uint8_t *)b - FTR);   // розмір тіла попереднього
    return (Block *)((uint8_t *)b - FTR - psize - HDR);
}
// Список вільних — простий стек: push на вершину, remove лінійним пошуком.
static void fl_push(Block *b) {
    b->free   = 1;
    b->next   = free_list;
    free_list = b;
}
static void fl_remove(Block *b) {
    if (free_list == b) { free_list = b->next; return; }
    for (Block *c = free_list; c; c = c->next)
        if (c->next == b) { c->next = b->next; return; }
}

// Один раз: уся арена — це один великий вільний блок.
void heap_init(void *mem, size_t total) {
    heap_start = (uint8_t *)mem;
    heap_end   = heap_start + total;
    free_list  = NULL;
    Block *b   = (Block *)heap_start;
    b->size    = total - HDR - FTR;
    set_footer(b);
    fl_push(b);
}

void *my_malloc(size_t n) {
    n = align_up(n);                                 // округлити вгору
    for (Block *b = free_list; b; b = b->next) {
        if (b->size < n) continue;                   // first-fit: перший, що влазить
        fl_remove(b);
        // хвіст вартий відрізати, лише якщо в ньому вміститься новий блок
        if (b->size >= n + HDR + FTR + THRESH) {
            size_t rest = b->size - n - HDR - FTR;
            b->size = n;
            set_footer(b);
            Block *tail = next_phys(b);              // хвіст лягає одразу за b
            tail->size  = rest;
            set_footer(tail);
            fl_push(tail);                           // і лишається вільним
        }
        b->free = 0;
        return body_of(b);                           // покажчик на тіло, за заголовком
    }
    return NULL;                                     // місця нема — чесно вертаємо NULL
}

void my_free(void *p) {
    if (p == NULL) return;
    Block *b = block_of(p);                          // відступ назад на заголовок
    b->free  = 1;

    Block *nxt = next_phys(b);
    if (nxt && nxt->free) {                           // злити з правим сусідом
        fl_remove(nxt);                              // спершу вийняти його зі списку
        b->size += HDR + FTR + nxt->size;            // поглинути його заголовок і footer
        set_footer(b);
    }
    Block *prv = prev_phys(b);
    if (prv && prv->free) {                           // злити з лівим сусідом
        fl_remove(prv);
        prv->size += HDR + FTR + b->size;
        set_footer(prv);
        b = prv;                                     // далі працюємо з об'єднаним блоком
    }
    fl_push(b);                                       // об'єднаний блок — у список вільних
}
