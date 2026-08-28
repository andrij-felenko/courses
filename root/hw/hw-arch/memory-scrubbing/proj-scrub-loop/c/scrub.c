/* scrub.c — програмне очищення ECC-SRAM на МК без апаратного патруля.
 *
 * Модель заліза (звірте з довідником!):
 *   • SRAM накрита SECDED, гранула — GRANULE байтів;
 *   • на читанні контролер виправляє поодинокий збій У ДАНИХ, що йдуть
 *     майстрові, але КОМІРКУ не переписує — це наш клопіт;
 *   • монітор ECC дає переривання на виправлений і на невиправний збій
 *     та регістри адреси й виправлених даних.
 */
#include <stdint.h>
#include <stddef.h>
#include "cmsis_compiler.h"     /* __LDREXW / __STREXW / __CLREX */
#include "ecc_hal.h"            /* ecc_failing_addr / _data_lo / _data_hi / _clear_sec */
#include "fail_safe.h"          /* system_fail_safe */

/* ── ділянка: межі беремо з лінкер-скрипта, а не з голови ─────────────── */
extern uint8_t __scrub_start__[];      /* вирівняно на гранулу */
extern uint8_t __scrub_end__[];

#define GRANULE          8u            /* ширина слова ECC, байтів */
#define TICK_HZ          1000u
#define PASS_SECONDS     60u
#define TICKS_PER_PASS   (TICK_HZ * PASS_SECONDS)
#define BURST_MAX        64u           /* стеля читань за один захід задачі */
#define DUE_ALARM        1000u         /* борг, за яким T уже не гарантовано */

static uint32_t g_granules;            /* гранул у ділянці */
static uint32_t g_cursor;              /* наступна гранула (лише задача) */
static uint32_t g_acc;                 /* акумулятор темпу (лише ISR) */
static volatile uint32_t g_due;        /* борг (ISR ↔ задача) */

static uint32_t g_passes, g_corrected, g_uncorrectable;

/* ── неподільний борг ─────────────────────────────────────────────────── */
static void due_add(uint32_t n)
{
    uint32_t v;
    do { v = __LDREXW(&g_due); } while (__STREXW(v + n, &g_due) != 0u);
}

static uint32_t due_take(uint32_t max)
{
    uint32_t v, got;
    do {
        v = __LDREXW(&g_due);
        got = (v < max) ? v : max;
        if (got == 0u) { __CLREX(); return 0u; }
    } while (__STREXW(v - got, &g_due) != 0u);
    return got;
}

/* ── один дотик: змусити пам'ять справді віддати гранулу ──────────────── */
static inline void scrub_touch(const void *addr)
{
    /* ширина читання не важить: контролер не вміє звірити пів гранули,
       тож будь-яке звертання підіймає всі 72 біти й перевіряє їх. */
    uint32_t v = *(const volatile uint32_t *)addr;
    __asm__ volatile ("" :: "r" (v));   /* значення «вжито» — читання не викинути */
}

static void scrub_one(void)
{
    scrub_touch(__scrub_start__ + (size_t)g_cursor * GRANULE);
    if (++g_cursor >= g_granules) {
        g_cursor = 0;
        g_passes++;
    }
}

/* ── темп: рівно g_granules кроків за TICKS_PER_PASS тіків ────────────── */
void scrub_init(void)
{
    g_granules = (uint32_t)((__scrub_end__ - __scrub_start__) / GRANULE);
    g_cursor = 0; g_acc = 0; g_due = 0;
}

void scrub_tick_isr(void)              /* таймер TICK_HZ; жодного доступу до SRAM */
{
    uint32_t n = 0;
    g_acc += g_granules;
    while (g_acc >= TICKS_PER_PASS) {
        g_acc -= TICKS_PER_PASS;
        n++;
    }
    if (n != 0u)
        due_add(n);
}

void scrub_poll(void)                  /* фонова задача / idle-хук */
{
    uint32_t n = due_take(BURST_MAX);
    while (n-- != 0u)
        scrub_one();
}

int scrub_falling_behind(void)         /* борг росте → T порушено, є що доповісти */
{
    return g_due > DUE_ALARM;
}

/* ── ремонт: нас розбудив ECC, отже є заради чого писати ──────────────── */
void ecc_sec_irq_handler(void)         /* поодинокий збій — виправний */
{
    uintptr_t addr = ecc_failing_addr();
    uint32_t  lo   = ecc_failing_data_lo();   /* УЖЕ виправлені дані */
    uint32_t  hi   = ecc_failing_data_hi();

    ecc_clear_sec(); /* спершу прапорець: інакше регістр адреси застрягне на першій події */
    g_corrected++;

    if (addr >= (uintptr_t)__scrub_start__ && addr < (uintptr_t)__scrub_end__) {
        /* Пишемо ГРАНУЛУ ЦІЛКОМ і одним доступом: часткового запису вистачить,
           щоб контролер сам поліз читати гранулу задля перерахунку контрольних
           бітів — зайве читання, зайва подія, зайва гонитва.
           Звірте в дизасемблері, що це справді один STRD на вирівняну адресу. */
        *(volatile uint64_t *)addr = ((uint64_t)hi << 32) | lo;
    }
}

void ecc_ded_irq_handler(void)         /* подвійний збій — лагодити нема чим */
{
    uintptr_t addr = ecc_failing_addr();
    g_uncorrectable++;
    /* дані вже втрачено; чесно спинитися краще, ніж рахувати сміття */
    system_fail_safe(addr);
}
