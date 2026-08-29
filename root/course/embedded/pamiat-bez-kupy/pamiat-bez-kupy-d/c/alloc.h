/*
 * alloc.h — детерміновані розподілювачі пам'яті для прошивки без купи.
 *
 *   fixed_pool_t   — блоковий пул фіксованого розміру: alloc/free за O(1),
 *                    нуль байтів метаданих у зайнятому блоці;
 *   pool_set_t     — каскад пулів на кілька градацій розміру;
 *   memory_arena_t — двостороння лінійна арена з контрольними точками.
 *
 * Модуль НЕ виділяє пам'ять сам: увесь простір приходить ззовні статичними
 * масивами. Жодного виклику malloc/free в жодній функції немає.
 */
#ifndef ALLOC_H
#define ALLOC_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

/* ------------------------------------------------------------------ */
/*  Блоковий пул фіксованого розміру                                    */
/* ------------------------------------------------------------------ */

/* Вузол вбудованого (intrusive) списку вільних блоків. Він лежить у тілі
   самого блоку, поки блок вільний; щойно блок віддано клієнтові, той пише
   туди свої дані й затирає зв'язок. Звідси нульовий оверхед метаданих. */
typedef struct pool_node {
    struct pool_node *next;
} pool_node_t;

typedef struct {
    uint8_t     *buffer;         /* початок статичного масиву пула        */
    size_t       block_size;     /* крок блоку після вирівнювання         */
    size_t       block_count;    /* скільки блоків умістилося в буфер     */
    pool_node_t *free_list;      /* голова списку вільних блоків          */
    size_t       free_count;     /* скільки блоків вільні зараз           */
    size_t       min_free_count; /* водяний знак: найменший запас за час роботи */
} fixed_pool_t;

/* Розмічає буфер на блоки. Кількість блоків НЕ передається, а виводиться з
   розміру буфера: інакше вирівнювання block_size вгору тихо виводило б
   останній блок за межі масиву. Повертає false, якщо буфер не вирівняний
   під вказівник або замалий бодай на один блок. */
bool   pool_init(fixed_pool_t *pool, void *buffer, size_t buffer_size, size_t block_size);

void  *pool_alloc(fixed_pool_t *pool);
bool   pool_free(fixed_pool_t *pool, void *ptr);
bool   pool_owns(const fixed_pool_t *pool, const void *ptr);

size_t pool_block_size(const fixed_pool_t *pool);
size_t pool_block_count(const fixed_pool_t *pool);
size_t pool_free_count(const fixed_pool_t *pool);
size_t pool_min_free_count(const fixed_pool_t *pool);

/* ------------------------------------------------------------------ */
/*  Мультипул: кілька градацій розміру блоку                            */
/* ------------------------------------------------------------------ */

#define POOL_SET_MAX_CLASSES 4u
#define POOL_SET_NONE        0xFFu

typedef struct {
    fixed_pool_t pools[POOL_SET_MAX_CLASSES];
    size_t       class_count;
    /* Таблиця «стеля степеня двійки -> індекс класу». Заповнюється під час
       pool_set_add, тож вибір класу під час роботи — це CLZ і одне читання. */
    uint8_t      class_by_log2[32];
} pool_set_t;

void  pool_set_init(pool_set_t *set);
/* Класи додають У ЗРОСТАЮЧОМУ порядку розміру блоку; порушення порядку —
   помилка конфігурації, функція поверне false. */
bool  pool_set_add(pool_set_t *set, void *buffer, size_t buffer_size, size_t block_size);
void *pool_set_alloc(pool_set_t *set, size_t size);
bool  pool_set_free(pool_set_t *set, void *ptr);

/* ------------------------------------------------------------------ */
/*  Двостороння лінійна арена                                           */
/* ------------------------------------------------------------------ */

typedef struct {
    uint8_t *buffer;
    size_t   capacity;
    size_t   lower;      /* нижній курсор: росте вгору, довші об'єкти кадру */
    size_t   upper;      /* верхній курсор: росте вниз, чернетки (scratch)  */
    size_t   peak_used;  /* пікова сума обох боків — для звіту про бюджет   */
} memory_arena_t;

bool   arena_init(memory_arena_t *arena, void *buffer, size_t capacity);

void  *arena_alloc_aligned(memory_arena_t *arena, size_t size, size_t alignment);
void  *arena_alloc(memory_arena_t *arena, size_t size);
/* Виділення масиву з перевіркою переповнення множення count * elem_size. */
void  *arena_alloc_array(memory_arena_t *arena, size_t count, size_t elem_size, size_t alignment);

void  *arena_alloc_scratch_aligned(memory_arena_t *arena, size_t size, size_t alignment);
void  *arena_alloc_scratch(memory_arena_t *arena, size_t size);

size_t arena_save(const memory_arena_t *arena);
void   arena_restore(memory_arena_t *arena, size_t mark);
size_t arena_scratch_save(const memory_arena_t *arena);
void   arena_scratch_restore(memory_arena_t *arena, size_t mark);

void   arena_scratch_reset(memory_arena_t *arena);
void   arena_reset(memory_arena_t *arena);

size_t arena_used(const memory_arena_t *arena);
size_t arena_available(const memory_arena_t *arena);
size_t arena_peak(const memory_arena_t *arena);

/* ------------------------------------------------------------------ */
/*  Неблокувальний варіант пула (реалізація в pool_atomic.c)            */
/* ------------------------------------------------------------------ */

/* Працює лише на ARMv7-M / ARMv8-M, де є пара LDREX/STREX. Викликати можна
   і з потоку, і з обробника переривання, не вимикаючи переривань узагалі.
   На інших цілях файл компілюється порожнім — користуйтеся pool_alloc під
   критичною секцією. */
void *pool_alloc_atomic(fixed_pool_t *pool);
bool  pool_free_atomic(fixed_pool_t *pool, void *ptr);

#endif /* ALLOC_H */
