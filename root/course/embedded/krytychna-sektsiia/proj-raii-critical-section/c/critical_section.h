#ifndef CRITICAL_SECTION_H
#define CRITICAL_SECTION_H

/*
 * Критичні секції для ARM Cortex-M.
 *
 * Увесь код інлайновий: ні виділення пам'яті, ні викликів через покажчик.
 * На платі "cmsis_compiler.h" — справжній заголовок CMSIS; у хостових тестах
 * замість нього підставляється заглушка c/test/cmsis_compiler.h через -I.
 */

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#include "cmsis_compiler.h"

#if !defined(__GNUC__) && !defined(__clang__) && !defined(__ARMCC_VERSION)
#  error "Потрібен GCC, Clang або ARM Compiler 6: спираємось на __attribute__((cleanup))"
#endif

/*
 * BASEPRI є лише на Cortex-M3/M4/M7/M33. Ознаку дає сам компілятор із -mcpu,
 * тому не чекаємо на заголовок пристрою з макросом __CORTEX_M.
 * Хостовий тест визначає CS_HAS_BASEPRI самостійно.
 */
#if !defined(CS_HAS_BASEPRI)
#  if defined(__ARM_ARCH_7M__) || defined(__ARM_ARCH_7EM__) || defined(__ARM_ARCH_8M_MAIN__)
#    define CS_HAS_BASEPRI 1
#  else
#    define CS_HAS_BASEPRI 0
#  endif
#endif

/*
 * Бар'єр оптимізації: забороняє компіляторові переносити доступи до пам'яті
 * через межу секції. Жодної інструкції не породжує.
 */
#define CS_BARRIER() __asm volatile("" ::: "memory")

/* --- 1. Глобальне маскування через PRIMASK (усі ядра Cortex-M) ----------- */

typedef struct {
    uint32_t primask;   /* стан маски ДО входу */
} critical_section_t;

static inline critical_section_t critical_section_enter(void)
{
    critical_section_t cs;
    cs.primask = __get_PRIMASK();
    __disable_irq();
    CS_BARRIER();
    return cs;
}

static inline void critical_section_exit(critical_section_t cs)
{
    CS_BARRIER();
    /*
     * Відновлюємо збережений стан, а не вмикаємо переривання беззастережно.
     * Саме це робить вкладення довільної глибини безпечним: вихід із
     * внутрішньої секції не відкриває переривань, поки триває зовнішня.
     */
    __set_PRIMASK(cs.primask);
}

/* --- 2. Автоматичне зняття блокування ----------------------------------- */
/*
 * __attribute__((cleanup)) кличе обробник, коли змінна виходить з області
 * видимості — байдуже, через кінець блоку, return, break чи goto. Це і є
 * відповідь на витік блокування: забути про вихід ніде.
 */
static inline void critical_section_cleanup_(const critical_section_t *cs)
{
    critical_section_exit(*cs);
}

#define CS_CAT_(a, b) a##b
#define CS_CAT(a, b)  CS_CAT_(a, b)

/*
 * Унікальне ім'я на кожне вживання макроса. __COUNTER__ розкривається один
 * раз — під час підстановки аргументу, — тому обидва вживання імені в тілі
 * дістають той самий токен, і два блоки в одному рядку не стикаються.
 */
#if defined(__COUNTER__)
#  define CS_ID(base) CS_CAT(base, __COUNTER__)
#else
#  define CS_ID(base) CS_CAT(base, __LINE__)
#endif

#define CS_BLOCK_IMPL_(csvar, oncevar)                                         \
    for (critical_section_t csvar                                              \
             __attribute__((cleanup(critical_section_cleanup_)))               \
             = critical_section_enter(),                                       \
             *oncevar = &csvar;                                                \
         oncevar != NULL;                                                      \
         oncevar = NULL)

/*
 * CRITICAL_BLOCK() { ... } — тіло виконується рівно один раз із вимкненими
 * перериваннями. Покажчик тримає єдину ітерацію, cleanup знімає блокування.
 */
#define CRITICAL_BLOCK() CS_BLOCK_IMPL_(CS_ID(cs_), CS_ID(cs_once_))

/* --- 3. Селективне маскування через BASEPRI ------------------------------ */

#if CS_HAS_BASEPRI

typedef struct {
    uint32_t basepri;
} priority_section_t;

/*
 * Поріг подано вже зміщеним у старші біти поля пріоритету NVIC
 * (0x50 — це пріоритет 5 при чотирьох значущих бітах).
 */
static inline priority_section_t priority_section_enter(uint32_t max_syscall_prio)
{
    priority_section_t ps;
    ps.basepri = __get_BASEPRI();
    /*
     * __set_BASEPRI_MAX записує нове значення лише тоді, коли воно посилює
     * маскування. Вкладений блок зі слабшим порогом не розмаскує переривань,
     * які закрив зовнішній.
     */
    __set_BASEPRI_MAX(max_syscall_prio);
    CS_BARRIER();
    return ps;
}

static inline void priority_section_exit(priority_section_t ps)
{
    CS_BARRIER();
    __set_BASEPRI(ps.basepri);
}

static inline void priority_section_cleanup_(const priority_section_t *ps)
{
    priority_section_exit(*ps);
}

#define CS_PRIO_BLOCK_IMPL_(psvar, oncevar, prio)                              \
    for (priority_section_t psvar                                              \
             __attribute__((cleanup(priority_section_cleanup_)))               \
             = priority_section_enter(prio),                                   \
             *oncevar = &psvar;                                                \
         oncevar != NULL;                                                      \
         oncevar = NULL)

#define PRIORITY_BLOCK(prio) CS_PRIO_BLOCK_IMPL_(CS_ID(ps_), CS_ID(ps_once_), (prio))

#endif /* CS_HAS_BASEPRI */

/* --- 4. Діагностика контексту виконання ---------------------------------- */

/* IPSR != 0 означає, що ядро зараз обробляє виняток або переривання. */
static inline bool in_interrupt_context(void)
{
    return __get_IPSR() != 0U;
}

/* --- 5. Cortex-M7: спільний із DMA буфер --------------------------------- */

#if defined(__DCACHE_PRESENT) && (__DCACHE_PRESENT == 1U)

#define CS_CACHE_LINE 32U

/*
 * Вимкнених переривань замало, коли буфер читає контролер DMA: свіжі байти
 * можуть лежати в L1 D-Cache, а DMA ходить по шині AXI просто в ОЗП.
 * Тому виштовхуємо рядки кешу ДО того, як переривання ввімкнено назад.
 * Адресу й довжину вирівнюємо на рядок кешу — CMSIS вимагає саме цього,
 * інакше сусідні дані в тому ж рядку буде зіпсовано.
 */
static inline void critical_section_exit_dma(critical_section_t cs, void *buf, size_t size)
{
    const uint32_t base  = (uint32_t)(uintptr_t)buf;
    const uint32_t start = base & ~(CS_CACHE_LINE - 1U);
    const uint32_t end   = (base + (uint32_t)size + CS_CACHE_LINE - 1U)
                           & ~(CS_CACHE_LINE - 1U);

    SCB_CleanDCache_by_Addr((uint32_t *)(uintptr_t)start, (int32_t)(end - start));
    __DSB();
    critical_section_exit(cs);
}

#endif /* __DCACHE_PRESENT */

#endif /* CRITICAL_SECTION_H */
