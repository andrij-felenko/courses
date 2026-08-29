/*
 * arena.c — двостороння лінійна арена.
 * Виділення — це зсув курсора; звільнення поодинці не існує в принципі.
 */
#include "alloc.h"

static bool is_power_of_two(size_t value)
{
    return value != 0u && (value & (value - 1u)) == 0u;
}

bool arena_init(memory_arena_t *arena, void *buffer, size_t capacity)
{
    if (arena == NULL || buffer == NULL || capacity == 0u) {
        return false;
    }
    arena->buffer    = (uint8_t *)buffer;
    arena->capacity  = capacity;
    arena->lower     = 0u;
    arena->upper     = capacity;
    arena->peak_used = 0u;
    return true;
}

static void note_peak(memory_arena_t *arena)
{
    const size_t used = arena->lower + (arena->capacity - arena->upper);
    if (used > arena->peak_used) {
        arena->peak_used = used;
    }
}

void *arena_alloc_aligned(memory_arena_t *arena, size_t size, size_t alignment)
{
    if (arena == NULL || arena->buffer == NULL || size == 0u) {
        return NULL;
    }
    if (!is_power_of_two(alignment)) {
        alignment = sizeof(uintptr_t);
    }

    const uintptr_t base    = (uintptr_t)arena->buffer;
    const uintptr_t cursor  = base + arena->lower;
    const uintptr_t aligned = (cursor + (uintptr_t)(alignment - 1u)) & ~(uintptr_t)(alignment - 1u);
    /* Межа знизу — не кінець буфера, а поточне положення верхнього курсора:
       вільний простір між боками спільний. */
    const uintptr_t limit   = base + arena->upper;

    if (aligned < cursor || aligned > limit) {
        return NULL;                          /* переповнення адреси або впертися в scratch */
    }
    if (size > (size_t)(limit - aligned)) {
        return NULL;                          /* арена замала для цього запиту */
    }

    arena->lower = (size_t)(aligned - base) + size;
    note_peak(arena);
    return (void *)aligned;
}

void *arena_alloc(memory_arena_t *arena, size_t size)
{
    return arena_alloc_aligned(arena, size, sizeof(uintptr_t));
}

void *arena_alloc_array(memory_arena_t *arena, size_t count, size_t elem_size, size_t alignment)
{
    if (count == 0u || elem_size == 0u) {
        return NULL;
    }
    /* Переповнення множення дало б крихітний буфер під величезний масив —
       класичний спосіб перетворити «немає пам'яті» на затирання сусідів. */
    if (count > (SIZE_MAX / elem_size)) {
        return NULL;
    }
    return arena_alloc_aligned(arena, count * elem_size, alignment);
}

void *arena_alloc_scratch_aligned(memory_arena_t *arena, size_t size, size_t alignment)
{
    if (arena == NULL || arena->buffer == NULL || size == 0u) {
        return NULL;
    }
    if (!is_power_of_two(alignment)) {
        alignment = sizeof(uintptr_t);
    }
    if (size > arena->upper) {
        return NULL;                          /* не вміститься навіть до нуля */
    }

    const uintptr_t base = (uintptr_t)arena->buffer;
    const uintptr_t top  = base + arena->upper;
    /* Верхній курсор рухається вниз, тому адресу вирівнюємо ВНИЗ. */
    const uintptr_t cand = (top - size) & ~(uintptr_t)(alignment - 1u);

    if (cand < base + arena->lower) {
        return NULL;                          /* курсори зустрілися */
    }

    arena->upper = (size_t)(cand - base);
    note_peak(arena);
    return (void *)cand;
}

void *arena_alloc_scratch(memory_arena_t *arena, size_t size)
{
    return arena_alloc_scratch_aligned(arena, size, sizeof(uintptr_t));
}

size_t arena_save(const memory_arena_t *arena)
{
    return arena ? arena->lower : 0u;
}

void arena_restore(memory_arena_t *arena, size_t mark)
{
    /* Контрольна точка вміє лише відкочувати назад: «відновлення» вперед
       віддало б клієнтові пам'ять, яку ніхто не виділяв. */
    if (arena != NULL && mark <= arena->lower) {
        arena->lower = mark;
    }
}

size_t arena_scratch_save(const memory_arena_t *arena)
{
    return arena ? arena->upper : 0u;
}

void arena_scratch_restore(memory_arena_t *arena, size_t mark)
{
    if (arena != NULL && mark >= arena->upper && mark <= arena->capacity) {
        arena->upper = mark;
    }
}

void arena_scratch_reset(memory_arena_t *arena)
{
    if (arena != NULL) {
        arena->upper = arena->capacity;
    }
}

void arena_reset(memory_arena_t *arena)
{
    if (arena != NULL) {
        arena->lower = 0u;
        arena->upper = arena->capacity;
        /* peak_used свідомо не скидаємо: це підсумок за весь час роботи. */
    }
}

size_t arena_used(const memory_arena_t *arena)
{
    return arena ? (arena->lower + (arena->capacity - arena->upper)) : 0u;
}

size_t arena_available(const memory_arena_t *arena)
{
    return arena ? (arena->upper - arena->lower) : 0u;
}

size_t arena_peak(const memory_arena_t *arena)
{
    return arena ? arena->peak_used : 0u;
}
