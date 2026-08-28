#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <assert.h>

/* Інтерфейс віртуального джерела часу */
typedef struct {
    uint16_t virtual_ticks_16;
    uint32_t virtual_ticks_32;
    uint64_t virtual_ticks_64;
} mock_clock_t;

static mock_clock_t g_mock_clock = {0};

void mock_clock_init(uint16_t start_16, uint32_t start_32) {
    g_mock_clock.virtual_ticks_16 = start_16;
    g_mock_clock.virtual_ticks_32 = start_32;
    g_mock_clock.virtual_ticks_64 = (uint64_t)start_32;
}

void mock_clock_advance_ms(uint32_t delta_ms) {
    g_mock_clock.virtual_ticks_16 = (uint16_t)(g_mock_clock.virtual_ticks_16 + delta_ms);
    g_mock_clock.virtual_ticks_32 += delta_ms;
    g_mock_clock.virtual_ticks_64 += delta_ms;
}

uint16_t mock_clock_get_16(void) { return g_mock_clock.virtual_ticks_16; }
uint32_t mock_clock_get_32(void) { return g_mock_clock.virtual_ticks_32; }

/* Безпечне атомарне зчитування 64-бітного часу з симуляцією захисту від гонок */
uint64_t mock_clock_get_64_safe(void) {
    uint32_t high1 = (uint32_t)(g_mock_clock.virtual_ticks_64 >> 32);
    uint32_t low   = (uint32_t)(g_mock_clock.virtual_ticks_64 & 0xFFFFFFFFULL);
    uint32_t high2 = (uint32_t)(g_mock_clock.virtual_ticks_64 >> 32);

    /* Якщо під час читання старше слово змінилося — перечитуємо заново */
    if (high1 != high2) {
        low   = (uint32_t)(g_mock_clock.virtual_ticks_64 & 0xFFFFFFFFULL);
        high2 = (uint32_t)(g_mock_clock.virtual_ticks_64 >> 32);
    }
    return ((uint64_t)high2 << 32) | low;
}

/* Тестований модуль безпекового наглядача серцебиття */
#define HEARTBEAT_TIMEOUT_MS  100U

typedef enum {
    WATCHDOG_OK = 0,
    WATCHDOG_TRIPPED = 1
} watchdog_state_t;

typedef struct {
    uint16_t last_heartbeat_16;
    uint32_t trip_count;
    watchdog_state_t state;
} safe_watchdog_t;

void safe_watchdog_init(safe_watchdog_t *wd, uint16_t now) {
    wd->last_heartbeat_16 = now;
    wd->trip_count = 0;
    wd->state = WATCHDOG_OK;
}

void safe_watchdog_feed(safe_watchdog_t *wd, uint16_t now) {
    wd->last_heartbeat_16 = now;
    wd->state = WATCHDOG_OK;
}

/* Коректна модульна перевірка дедлайну без пасток знакового приведення */
watchdog_state_t safe_watchdog_check(safe_watchdog_t *wd, uint16_t now) {
    uint16_t elapsed = (uint16_t)(now - wd->last_heartbeat_16);
    if (elapsed > HEARTBEAT_TIMEOUT_MS) {
        wd->state = WATCHDOG_TRIPPED;
        wd->trip_count++;
    } else {
        wd->state = WATCHDOG_OK;
    }
    return wd->state;
}

/* =========================================================================
   Тестові сценарії
   ========================================================================= */

static void test_normal_operation(void) {
    printf("[TEST] 1. Штатна робота без переповнення... ");
    mock_clock_init(1000, 1000);
    safe_watchdog_t wd;
    safe_watchdog_init(&wd, mock_clock_get_16());

    /* Оновлення кожні 20 мс */
    for (int i = 0; i < 5; ++i) {
        mock_clock_advance_ms(20);
        watchdog_state_t st = safe_watchdog_check(&wd, mock_clock_get_16());
        assert(st == WATCHDOG_OK);
        safe_watchdog_feed(&wd, mock_clock_get_16());
    }
    printf("PASSED\n");
}

static void test_rollover_seamless_feed(void) {
    printf("[TEST] 2. Стрибок через нуль (0xFFFA -> 0x000A) з регулярним годуванням... ");
    /* Початковий час: за 6 мс до переповнення 16-бітного лічильника (65530) */
    mock_clock_init(65530U, 65530U);
    safe_watchdog_t wd;
    safe_watchdog_init(&wd, mock_clock_get_16());

    /* Крок 1: час переходить у 65535 (+5 мс) */
    mock_clock_advance_ms(5);
    assert(mock_clock_get_16() == 65535U);
    assert(safe_watchdog_check(&wd, mock_clock_get_16()) == WATCHDOG_OK);

    /* Крок 2: час переходить через 0 у 10 (+11 мс від 65535 -> 10) */
    mock_clock_advance_ms(11);
    assert(mock_clock_get_16() == 10U);
    
    /* Дельта: (uint16_t)(10 - 65530) = 16 мс. Повинно бути менше ніж 100 мс */
    watchdog_state_t st = safe_watchdog_check(&wd, mock_clock_get_16());
    assert(st == WATCHDOG_OK);

    /* Годуємо сторожа на позначці 10 */
    safe_watchdog_feed(&wd, mock_clock_get_16());

    /* Крок 3: просуваємося ще на 50 мс */
    mock_clock_advance_ms(50);
    assert(safe_watchdog_check(&wd, mock_clock_get_16()) == WATCHDOG_OK);
    printf("PASSED\n");
}

static void test_rollover_actual_timeout(void) {
    printf("[TEST] 3. Справжній таймаут зв'язку через точку переповнення... ");
    /* Останній пакет отримано на позначці 65500 */
    mock_clock_init(65500U, 65500U);
    safe_watchdog_t wd;
    safe_watchdog_init(&wd, mock_clock_get_16());

    /* Минає 105 мс без надходження пакетів -> новий час 65500 + 105 = 69 (0x0045) */
    mock_clock_advance_ms(105);
    assert(mock_clock_get_16() == 69U);

    /* Перевірка: (uint16_t)(69 - 65500) = 105 > 100 -> Спрацьовування захисту! */
    watchdog_state_t st = safe_watchdog_check(&wd, mock_clock_get_16());
    assert(st == WATCHDOG_TRIPPED);
    assert(wd.trip_count == 1);
    printf("PASSED\n");
}

static void test_fuzzing_around_boundary(void) {
    printf("[TEST] 4. Фазинг псевдовипадкових інтервалів навколо межі 65535... ");
    mock_clock_init(65400U, 65400U);
    safe_watchdog_t wd;
    safe_watchdog_init(&wd, mock_clock_get_16());

    /* Імітуємо 1000 циклів обміну з випадковими кроками 5..30 мс */
    uint32_t pseudo_rand = 0x12345678U;
    for (int i = 0; i < 1000; ++i) {
        pseudo_rand = pseudo_rand * 1103515245U + 12345U;
        uint32_t step_ms = 5 + (pseudo_rand % 25); /* 5..29 мс */

        mock_clock_advance_ms(step_ms);
        watchdog_state_t st = safe_watchdog_check(&wd, mock_clock_get_16());
        assert(st == WATCHDOG_OK);
        safe_watchdog_feed(&wd, mock_clock_get_16());
    }
    printf("PASSED (1000 ітерацій)\n");
}

int main(void) {
    printf("=== Запуск регресійного стенду Time-Warp Virtual HAL ===\n");
    test_normal_operation();
    test_rollover_seamless_feed();
    test_rollover_actual_timeout();
    test_fuzzing_around_boundary();
    printf("=== Усі 4 тести пройдено успішно. Дефектів не виявлено. ===\n");
    return 0;
}
