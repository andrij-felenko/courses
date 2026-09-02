#ifndef CS_ASM_H
#define CS_ASM_H

/*
 * C-оголошення асемблерного шару (libcsasm.a).
 *
 * Це позаінлайнові двійники інтринсиків CMSIS. Інлайнова версія з
 * critical_section.h швидша (компілятор бачить її наскрізь), але
 * позаінлайнова має рівно передбачувану ціну — саме її міряють, коли треба
 * назвати вартість входу в секцію в тактах, і саме вона потрібна, коли
 * секцію відкриває код, зібраний іншим компілятором.
 */

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
#  define CS_STATIC_ASSERT(cond, msg) static_assert(cond, msg)
extern "C" {
#else
#  define CS_STATIC_ASSERT(cond, msg) _Static_assert(cond, msg)
#endif

/* --- PRIMASK: глобальне маскування (усі ядра Cortex-M) ------------------- */

uint32_t cs_get_primask(void);
void     cs_set_primask(uint32_t value);
void     cs_disable_irq(void);
void     cs_enable_irq(void);

/* Вхід повертає стан маски ДО себе; вихід його відновлює, а не вмикає
   переривання беззастережно — саме це робить вкладення безпечним. */
uint32_t cs_enter(void);
void     cs_exit(uint32_t saved);

/* Те саме з DSB/ISB: потрібно, коли одразу після межі секції йде запис у
   периферію або зміна таблиці векторів. Коштує на кілька тактів більше. */
uint32_t cs_enter_sync(void);
void     cs_exit_sync(uint32_t saved);

/* --- BASEPRI: селективне маскування (Cortex-M3/M4/M7/M33) ---------------- */

uint32_t cs_get_basepri(void);
void     cs_set_basepri(uint32_t value);
void     cs_set_basepri_max(uint32_t value);

uint32_t cs_prio_enter(uint32_t threshold);
void     cs_prio_exit(uint32_t saved);

/* Скільки бітів пріоритету реалізовано в цьому кристалі (типово 3–4 з 8).
   Дізнається дослідом, тому кличемо один раз на старті. */
uint32_t cs_prio_bits(void);

/* Логічний рівень (0 — найвищий) у значення для BASEPRI: зсув у старші
   біти байта. При чотирьох реалізованих бітах рівень 5 дає 0x50. */
uint32_t cs_prio_encode(uint32_t level);

/* --- Контекст виконання --------------------------------------------------- */

uint32_t cs_get_ipsr(void);           /* 0 — потоковий режим              */
bool     cs_in_interrupt_context(void);
uint32_t cs_get_control(void);
bool     cs_is_privileged(void);

/* --- Кеш даних Cortex-M7 -------------------------------------------------- */
/*
 * Потрібні лише тоді, коли буфер після секції читає або пише DMA.
 * Модуль збирається, коли визначено CS_HAS_DCACHE.
 */

uint32_t cs_dcache_line_size(void);
void     cs_dcache_clean_range(const void *addr, uint32_t size);
void     cs_dcache_invalidate_range(const void *addr, uint32_t size);
void     cs_dcache_clean_invalidate_range(const void *addr, uint32_t size);
void     cs_icache_invalidate_all(void);

/* --- Профілювання лічильником тактів -------------------------------------- */

bool     cs_dwt_enable(void);         /* false — лічильника немає/не біжить */
uint32_t cs_dwt_cycles(void);
bool     cs_debugger_attached(void);

/* Ціна пари «замаскувати — відновити» в тактах, за вирахуванням вартості
   самого вимірювання. На Cortex-M4 віддає 3. */
uint32_t cs_measure_enter_exit(void);

/* Виконати body(ctx) під маскою й повернути тривалість у тактах. */
uint32_t cs_profile_call(void (*body)(void *), void *ctx);

/* --- Самоперевірка на старті ---------------------------------------------- */
/*
 * Повертає 0, коли все гаразд, інакше — набір бітів нижче. Кличеться з
 * потокового режиму до запуску планувальника: усередині переривання на
 * короткий час вмикаються, а наприкінці стан маски повертається як був.
 */
#define CS_SELFTEST_SAVED_STATE   (1U << 0)  /* enter не віддав старий стан */
#define CS_SELFTEST_NOT_MASKED    (1U << 1)  /* після enter маска не стоїть */
#define CS_SELFTEST_NOT_RESTORED  (1U << 2)  /* exit не відновив стан       */
#define CS_SELFTEST_NESTING       (1U << 3)  /* вкладений вихід розмаскував */
#define CS_SELFTEST_PRIO_WEAKENED (1U << 4)  /* BASEPRI_MAX послабив поріг  */
#define CS_SELFTEST_PRIO_SET      (1U << 5)  /* поріг не встановлюється     */
#define CS_SELFTEST_CONTEXT       (1U << 6)  /* IPSR бреше в потоці         */
#define CS_SELFTEST_DWT           (1U << 7)  /* лічильник тактів не біжить  */

uint32_t cs_selftest(void);

/* --- Навігація, написана руками ------------------------------------------- */
/*
 * Асемблерні функції знають розкладку структури числами, тому розкладку
 * стереже перевірка на етапі компіляції: варто комусь переставити поле —
 * і збірка стане тут, а не мовчки віддасть радіоканалу сміття.
 */

typedef struct {
    int32_t  latitude;      /* 1e-7 градуса */
    int32_t  longitude;     /* 1e-7 градуса */
    int32_t  altitude_mm;
    uint64_t timestamp_us;
} nav_fix_t;

typedef struct {
    nav_fix_t fix;
    bool      has_fix;
    uint32_t  updates;
} nav_state_t;

CS_STATIC_ASSERT(offsetof(nav_fix_t, timestamp_us) == 16,
                 "nav_update.S читає мітку часу як ldrd [r1, #16]");
CS_STATIC_ASSERT(sizeof(nav_fix_t) == 24,
                 "nav_update.S копіює рівно 24 байти фікса");
CS_STATIC_ASSERT(offsetof(nav_state_t, has_fix) == 24,
                 "nav_update.S пише прапорець як strb [r0, #24]");
CS_STATIC_ASSERT(offsetof(nav_state_t, updates) == 28,
                 "nav_update.S крутить лічильник за зсувом 28");

void nav_asm_update(nav_state_t *self, const nav_fix_t *fix);
bool nav_asm_snapshot(const nav_state_t *self, nav_fix_t *out);
uint32_t nav_asm_updates(const nav_state_t *self);
void nav_asm_reset(nav_state_t *self);

#ifdef __cplusplus
}
#endif

#endif /* CS_ASM_H */
