/*
 * pool.c — блоковий пул фіксованого розміру та каскад пулів.
 * Уся робота — це кілька інструкцій зі списком; жодних проходів по пам'яті.
 */
#include "alloc.h"

static size_t align_up(size_t value, size_t align)
{
    return (value + (align - 1u)) & ~(align - 1u);
}

/* Стеля двійкового логарифма. На Cortex-M це одна інструкція CLZ. */
static unsigned ceil_log2(size_t value)
{
    if (value <= 1u) {
        return 0u;
    }
#if defined(__GNUC__)
    return (unsigned)(32 - __builtin_clz((unsigned)(value - 1u)));
#else
    unsigned lg = 0u;
    while (((size_t)1u << lg) < value) {
        ++lg;
    }
    return lg;
#endif
}

bool pool_init(fixed_pool_t *pool, void *buffer, size_t buffer_size, size_t block_size)
{
    if (pool == NULL || buffer == NULL || block_size == 0u) {
        return false;
    }

    const size_t align = sizeof(uintptr_t);

    /* У тілі вільного блоку лежатиме вказівник, тож початок буфера мусить
       бути вирівняний. Мовчки зсунути початок не можна: тоді розрахований
       у відомості бюджет пам'яті перестав би збігатися з фактичним. */
    if (((uintptr_t)buffer & (uintptr_t)(align - 1u)) != 0u) {
        return false;
    }

    size_t step = align_up(block_size, align);
    if (step < sizeof(pool_node_t)) {
        step = sizeof(pool_node_t);   /* блок мусить умістити вузол списку */
    }

    const size_t count = buffer_size / step;
    if (count == 0u) {
        return false;                 /* буфер не тягне навіть одного блоку */
    }

    pool->buffer         = (uint8_t *)buffer;
    pool->block_size     = step;
    pool->block_count    = count;
    pool->free_count     = count;
    pool->min_free_count = count;
    pool->free_list      = NULL;

    /* Список будуємо з хвоста, щоб перші видачі йшли за зростанням адрес:
       у дампі пам'яті такий пул читається набагато легше. */
    for (size_t i = count; i-- > 0u;) {
        pool_node_t *node = (pool_node_t *)(void *)(pool->buffer + (i * step));
        node->next      = pool->free_list;
        pool->free_list = node;
    }

    return true;
}

void *pool_alloc(fixed_pool_t *pool)
{
    if (pool == NULL || pool->free_list == NULL) {
        return NULL;                  /* пул вичерпано — це нормальний стан */
    }

    pool_node_t *node = pool->free_list;
    pool->free_list   = node->next;
    pool->free_count--;

    if (pool->free_count < pool->min_free_count) {
        pool->min_free_count = pool->free_count;
    }

    return (void *)node;
}

bool pool_owns(const fixed_pool_t *pool, const void *ptr)
{
    if (pool == NULL || ptr == NULL || pool->buffer == NULL) {
        return false;
    }

    const uint8_t *p     = (const uint8_t *)ptr;
    const uint8_t *start = pool->buffer;
    const uint8_t *end   = pool->buffer + (pool->block_size * pool->block_count);

    if (p < start || p >= end) {
        return false;
    }
    /* Вказівник мусить дивитися на ПОЧАТОК блоку: адреса всередині блоку
       означає, що клієнт передав щось інше — наприклад, поле структури. */
    return (((size_t)(p - start)) % pool->block_size) == 0u;
}

bool pool_free(fixed_pool_t *pool, void *ptr)
{
    if (!pool_owns(pool, ptr)) {
        return false;                 /* чужа адреса — ланцюжок не чіпаємо */
    }
    if (pool->free_count >= pool->block_count) {
        return false;                 /* усі блоки й так вільні: явне подвійне звільнення */
    }

    /* Повного захисту від подвійного звільнення тут немає: перевірка вимагала б
       проходу по списку вільних, тобто O(N), і зламала б головну обіцянку пула.
       Дисципліна виклику: звільнив — занулив свій вказівник. */
    pool_node_t *node = (pool_node_t *)ptr;
    node->next        = pool->free_list;
    pool->free_list   = node;
    pool->free_count++;

    return true;
}

size_t pool_block_size(const fixed_pool_t *pool)     { return pool ? pool->block_size : 0u; }
size_t pool_block_count(const fixed_pool_t *pool)    { return pool ? pool->block_count : 0u; }
size_t pool_free_count(const fixed_pool_t *pool)     { return pool ? pool->free_count : 0u; }
size_t pool_min_free_count(const fixed_pool_t *pool) { return pool ? pool->min_free_count : 0u; }

/* ------------------------------------------------------------------ */
/*  Каскад пулів                                                        */
/* ------------------------------------------------------------------ */

void pool_set_init(pool_set_t *set)
{
    if (set == NULL) {
        return;
    }
    set->class_count = 0u;
    for (unsigned lg = 0u; lg < 32u; ++lg) {
        set->class_by_log2[lg] = POOL_SET_NONE;
    }
}

bool pool_set_add(pool_set_t *set, void *buffer, size_t buffer_size, size_t block_size)
{
    if (set == NULL || set->class_count >= POOL_SET_MAX_CLASSES) {
        return false;
    }

    const size_t index = set->class_count;
    if (index > 0u && block_size <= pool_block_size(&set->pools[index - 1u])) {
        return false;                 /* класи мусять зростати */
    }
    if (!pool_init(&set->pools[index], buffer, buffer_size, block_size)) {
        return false;
    }

    /* Заповнюємо таблицю пошуку: для кожного степеня двійки, який цей клас
       здатен покрити й який ще нікому не належить, ставимо його індекс.
       Класи додаються за зростанням, тож перший, хто зайняв комірку, і є
       найменшим придатним. */
    const size_t step = pool_block_size(&set->pools[index]);
    for (unsigned lg = 0u; lg < 32u; ++lg) {
        if (set->class_by_log2[lg] == POOL_SET_NONE && ((size_t)1u << lg) <= step) {
            set->class_by_log2[lg] = (uint8_t)index;
        }
    }

    set->class_count++;
    return true;
}

void *pool_set_alloc(pool_set_t *set, size_t size)
{
    if (set == NULL || size == 0u) {
        return NULL;
    }

    const unsigned lg = ceil_log2(size);
    if (lg >= 32u) {
        return NULL;
    }

    const uint8_t index = set->class_by_log2[lg];
    if (index == POOL_SET_NONE) {
        return NULL;                  /* запит більший за найбільший клас */
    }

    /* Округлення запиту вгору до степеня двійки — плата за вибір класу за
       константний час: запит на 33 байти піде в клас 128, якщо класу 64 немає.
       І свідомо НЕ падаємо у старший клас, коли свій порожній: інакше сплеск
       дрібних запитів з'їв би блоки, на які розрахувала інша підсистема, і
       статичний бюджет перестав би бути гарантією. */
    return pool_alloc(&set->pools[index]);
}

bool pool_set_free(pool_set_t *set, void *ptr)
{
    if (set == NULL || ptr == NULL) {
        return false;
    }
    for (size_t i = 0u; i < set->class_count; ++i) {
        if (pool_owns(&set->pools[i], ptr)) {
            return pool_free(&set->pools[i], ptr);
        }
    }
    return false;                     /* адреса не з цього каскаду */
}
