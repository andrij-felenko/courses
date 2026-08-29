/*
 * pool_atomic.c — той самий блоковий пул, але без вимкнення переривань.
 *
 * Пара LDREX/STREX (ARMv7-M, ARMv8-M) дає ексклюзивний доступ: якщо між
 * читанням і записом сталося переривання чи перемикання контексту, монітор
 * ексклюзивності скидається, STREX повертає 1 і цикл просто повторюється.
 * Затримка реакції на переривання при цьому не зростає ані на такт.
 */
#include "alloc.h"

#if defined(__ARM_ARCH_7M__) || defined(__ARM_ARCH_7EM__) || \
    defined(__ARM_ARCH_8M_MAIN__) || defined(__ARM_ARCH_8M_BASE__)

#include "cmsis_compiler.h"   /* __LDREXW, __STREXW, __CLREX, __DMB із CMSIS-Core */

_Static_assert(sizeof(size_t) == 4u, "LDREX/STREX працюють зі словом у 32 біти");
_Static_assert(sizeof(pool_node_t *) == 4u, "вказівник мусить бути словом");

/* Лічильники теж мусять мінятися атомарно: інакше два потоки, що взяли
   блоки одночасно, зменшать free_count лише один раз, і звіт про бюджет
   почне брехати саме там, де на нього покладаються. */
static void atomic_take_one(fixed_pool_t *pool)
{
    uint32_t value;
    do {
        value = __LDREXW((volatile uint32_t *)&pool->free_count);
    } while (__STREXW(value - 1u, (volatile uint32_t *)&pool->free_count) != 0u);

    const uint32_t left = value - 1u;
    uint32_t seen_min;
    do {
        seen_min = __LDREXW((volatile uint32_t *)&pool->min_free_count);
        if (seen_min <= left) {
            __CLREX();               /* водяний знак уже нижчий — нічого писати */
            return;
        }
    } while (__STREXW(left, (volatile uint32_t *)&pool->min_free_count) != 0u);
}

static void atomic_give_one(fixed_pool_t *pool)
{
    uint32_t value;
    do {
        value = __LDREXW((volatile uint32_t *)&pool->free_count);
    } while (__STREXW(value + 1u, (volatile uint32_t *)&pool->free_count) != 0u);
}

void *pool_alloc_atomic(fixed_pool_t *pool)
{
    if (pool == NULL) {
        return NULL;
    }

    pool_node_t *head;
    pool_node_t *next;

    do {
        head = (pool_node_t *)__LDREXW((volatile uint32_t *)&pool->free_list);
        if (head == NULL) {
            __CLREX();               /* монітор треба зняти явно, інакше він
                                        зіпсує чужу пару LDREX/STREX */
            return NULL;
        }
        next = head->next;
    } while (__STREXW((uint32_t)next, (volatile uint32_t *)&pool->free_list) != 0u);

    __DMB();                         /* голова оновлена — далі йдуть дані клієнта */
    atomic_take_one(pool);
    return (void *)head;
}

bool pool_free_atomic(fixed_pool_t *pool, void *ptr)
{
    /* Перевірка меж і кроку читає лише незмінні поля пула, тож її можна
       робити поза ексклюзивним вікном. */
    if (!pool_owns(pool, ptr)) {
        return false;
    }

    pool_node_t *node = (pool_node_t *)ptr;
    pool_node_t *head;

    do {
        head = (pool_node_t *)__LDREXW((volatile uint32_t *)&pool->free_list);
        /* Запис у node->next іде за іншою адресою. Архітектура дозволяє
           монітору зніматися й від такого запису — тоді STREX просто дасть
           збій і ми пройдемо коло ще раз; помилки з цього не буде. */
        node->next = head;
        __DMB();                     /* next мусить стати видимим ДО публікації голови */
    } while (__STREXW((uint32_t)node, (volatile uint32_t *)&pool->free_list) != 0u);

    atomic_give_one(pool);
    return true;
}

/*
 * Про ABA. Класична пастка списків без блокувань: поки ми тримаємо head,
 * переривання встигає зняти два блоки й повернути перший — голова знову та
 * сама, а next уже інший. На Cortex-M цього не станеться: вхід у виняток і
 * повернення з нього скидають монітор ексклюзивності, тож наш STREX
 * гарантовано дасть збій. На багатоядерній машині зі звичайним CAS такої
 * гарантії немає — там до вказівника довелося б чіпляти лічильник поколінь.
 */

#else

/* Ціль без LDREX/STREX: чесно віддаємо відмову, щоб виклик не створив
   ілюзії атомарності. Там користуйтеся pool_alloc під критичною секцією. */
void *pool_alloc_atomic(fixed_pool_t *pool)
{
    (void)pool;
    return NULL;
}

bool pool_free_atomic(fixed_pool_t *pool, void *ptr)
{
    (void)pool;
    (void)ptr;
    return false;
}

#endif
