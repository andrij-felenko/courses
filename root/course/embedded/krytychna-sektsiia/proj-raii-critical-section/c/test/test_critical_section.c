/*
 * Хостові тести драйвера критичних секцій — жодної плати не треба.
 *
 *   gcc -std=c11 -Wall -Wextra -Ic/test -Ic \
 *       c/test/test_critical_section.c -o build/test_cs && ./build/test_cs
 *
 * Модуль навігації підключаємо ВИХІДНИКОМ: його стан статичний, і тест має
 * бачити рівно те саме, що бачить драйвер.
 */

#include <stdio.h>

#include "cmsis_compiler.h"
#include "../critical_section.h"
#include "../navigation.c"

static int g_failures;

#define CHECK(cond)                                                            \
    do {                                                                       \
        if (!(cond)) {                                                         \
            printf("ПРОВАЛ (рядок %d): %s\n", __LINE__, #cond);                \
            g_failures++;                                                      \
        }                                                                      \
    } while (0)

/* --- Фейкові драйвери плати ---------------------------------------------- */

static navigation_data_t g_gnss_fix;
static bool              g_gnss_ready;
static navigation_data_t g_sent;
static uint32_t          g_sent_count;

bool gnss_read_fix(navigation_data_t *out)
{
    if (!g_gnss_ready) {
        return false;
    }
    *out = g_gnss_fix;
    return true;
}

void radio_send(const navigation_data_t *fix)
{
    g_sent = *fix;
    g_sent_count++;
}

/* --- Перевірки ------------------------------------------------------------ */

static void test_save_restore(void)
{
    cmsis_mock_reset();

    CRITICAL_BLOCK() {
        CHECK(__get_PRIMASK() == 1U);
    }

    CHECK(__get_PRIMASK() == 0U);
    CHECK(g_mock.disable_calls == 1U);
    CHECK(g_mock.restore_calls == 1U);
    CHECK(g_mock.depth == 0U);
}

static void test_nesting(void)
{
    cmsis_mock_reset();

    CRITICAL_BLOCK() {
        CRITICAL_BLOCK() {
            CHECK(__get_PRIMASK() == 1U);
        }
        /* Вихід із вкладеної секції НЕ відкриває переривань. */
        CHECK(__get_PRIMASK() == 1U);
    }

    CHECK(__get_PRIMASK() == 0U);
    CHECK(g_mock.max_depth == 2U);
    CHECK(g_mock.depth == 0U);
}

static bool lookup_with_early_return(bool found)
{
    CRITICAL_BLOCK() {
        if (!found) {
            return false;
        }
    }
    return true;
}

static void test_early_return_does_not_leak(void)
{
    cmsis_mock_reset();

    CHECK(lookup_with_early_return(false) == false);
    CHECK(__get_PRIMASK() == 0U);   /* блокування не витекло */
    CHECK(g_mock.depth == 0U);

    CHECK(lookup_with_early_return(true) == true);
    CHECK(__get_PRIMASK() == 0U);
}

static void test_basepri_never_weakens(void)
{
    cmsis_mock_reset();

    PRIORITY_BLOCK(0x50U) {
        CHECK(__get_BASEPRI() == 0x50U);
        PRIORITY_BLOCK(0x70U) {
            /* Слабший поріг не має послабити чинне маскування. */
            CHECK(__get_BASEPRI() == 0x50U);
        }
        CHECK(__get_BASEPRI() == 0x50U);
        CHECK(__get_PRIMASK() == 0U);   /* BASEPRI не чіпає PRIMASK */
    }

    CHECK(__get_BASEPRI() == 0x00U);
}

static void test_interrupt_context_flag(void)
{
    cmsis_mock_reset();
    CHECK(in_interrupt_context() == false);

    g_mock.ipsr = 22U;   /* вдаємо, що ядро в обробнику */
    CHECK(in_interrupt_context() == true);
    g_mock.ipsr = 0U;
}

static void test_navigation_snapshot(void)
{
    const navigation_data_t fix = { 501234567, 306543210, 152300, 1724930000000000ULL };
    navigation_data_t snapshot;

    cmsis_mock_reset();
    navigation_init();

    CHECK(navigation_get_snapshot(&snapshot) == false);   /* фікса ще немає */
    CHECK(navigation_get_snapshot(NULL) == false);

    navigation_update(&fix);
    navigation_update(NULL);                               /* має бути безпечно */

    CHECK(navigation_get_snapshot(&snapshot) == true);
    CHECK(snapshot.latitude == fix.latitude);
    CHECK(snapshot.longitude == fix.longitude);
    CHECK(snapshot.altitude_mm == fix.altitude_mm);
    CHECK(snapshot.timestamp_us == fix.timestamp_us);
    CHECK(navigation_updates() == 1U);
    CHECK(__get_PRIMASK() == 0U);
}

static void test_isr_path(void)
{
    navigation_data_t snapshot;

    cmsis_mock_reset();
    navigation_init();
    g_sent_count = 0U;

    g_gnss_ready = true;
    g_gnss_fix.latitude     = 500000000;
    g_gnss_fix.longitude    = 300000000;
    g_gnss_fix.altitude_mm  = 100000;
    g_gnss_fix.timestamp_us = 1000000ULL;
    GNSS_IRQHandler();

    /* Наступний кадр прийшов битий — попередній фікс має вціліти. */
    g_gnss_ready = false;
    GNSS_IRQHandler();

    CHECK(navigation_updates() == 1U);
    CHECK(navigation_get_snapshot(&snapshot) == true);
    CHECK(snapshot.timestamp_us == 1000000ULL);

    telemetry_step();
    CHECK(g_sent_count == 1U);
    CHECK(g_sent.latitude == 500000000);
    CHECK(__get_PRIMASK() == 0U);
}

int main(void)
{
    test_save_restore();
    test_nesting();
    test_early_return_does_not_leak();
    test_basepri_never_weakens();
    test_interrupt_context_flag();
    test_navigation_snapshot();
    test_isr_path();

    if (g_failures == 0) {
        printf("усі перевірки пройдено\n");
        return 0;
    }
    printf("провалено перевірок: %d\n", g_failures);
    return 1;
}
