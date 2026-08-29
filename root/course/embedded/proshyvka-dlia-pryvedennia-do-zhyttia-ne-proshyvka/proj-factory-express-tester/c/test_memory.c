/* Маршовий тест March C- на виділеному статичному буфері.
 * Стек і таблиця векторів у тест не потрапляють — інакше контролер
 * звалиться в HardFault на першій же інверсній масці. */

#include "fct.h"
#include "hal.h"

#define RAM_TEST_WORDS 1024u
#define PATTERN_ZERO   0x00000000u
#define PATTERN_ONE    0xFFFFFFFFu

/* volatile обов'язковий: без нього компілятор викине «зайві» читання,
 * і марш перевірятиме оптимізатор, а не кремній. */
static volatile uint32_t s_ram[RAM_TEST_WORDS];

static void fill(uint32_t value)
{
    for (uint32_t i = 0; i < RAM_TEST_WORDS; i++) {
        s_ram[i] = value;
    }
}

/* Прямий прохід: читаємо expect, пишемо write. Повертає індекс дефекту
 * або -1, якщо фаза чиста. */
static int32_t march_up(uint32_t expect, uint32_t write)
{
    for (uint32_t i = 0; i < RAM_TEST_WORDS; i++) {
        if (s_ram[i] != expect) {
            return (int32_t)i;
        }
        s_ram[i] = write;
    }
    return -1;
}

static int32_t march_down(uint32_t expect, uint32_t write)
{
    for (uint32_t i = RAM_TEST_WORDS; i > 0; i--) {
        uint32_t idx = i - 1;
        if (s_ram[idx] != expect) {
            return (int32_t)idx;
        }
        s_ram[idx] = write;
    }
    return -1;
}

static int32_t march_verify(uint32_t expect)
{
    for (uint32_t i = 0; i < RAM_TEST_WORDS; i++) {
        if (s_ram[i] != expect) {
            return (int32_t)i;
        }
    }
    return -1;
}

void test_ram_march(fct_verdict_t *v)
{
    /* Переривання на час маршу замасковані: обробник, що торкнеться
     * буфера чи просто затримає прохід, зіпсує картину дефектів. */
    uint32_t primask = hal_irq_disable();
    int32_t bad = -1;
    const char *detail = NULL;

    fill(PATTERN_ZERO);                       /* фаза 1: ↕(w0) */
    hal_watchdog_kick();

    bad = march_up(PATTERN_ZERO, PATTERN_ONE);   /* фаза 2: ⇑(r0,w1) */
    if (bad >= 0) {
        detail = "SAF0 / TF: комірка не тримає 0";
    }
    hal_watchdog_kick();

    if (bad < 0) {
        bad = march_up(PATTERN_ONE, PATTERN_ZERO);   /* фаза 3: ⇑(r1,w0) */
        if (bad >= 0) {
            detail = "SAF1 / TF: комірка не переходить у 1";
        }
        hal_watchdog_kick();
    }
    if (bad < 0) {
        bad = march_down(PATTERN_ZERO, PATTERN_ONE); /* фаза 4: ⇓(r0,w1) */
        if (bad >= 0) {
            detail = "CF / AF: вплив сусідньої комірки на зворотному ході";
        }
        hal_watchdog_kick();
    }
    if (bad < 0) {
        bad = march_down(PATTERN_ONE, PATTERN_ZERO); /* фаза 5: ⇓(r1,w0) */
        if (bad >= 0) {
            detail = "CF: зворотний ємнісний зв'язок між комірками";
        }
        hal_watchdog_kick();
    }
    if (bad < 0) {
        bad = march_verify(PATTERN_ZERO);            /* фаза 6: ↕(r0) */
        if (bad >= 0) {
            detail = "Data retention: нуль не втримався до кінця маршу";
        }
    }

    hal_irq_restore(primask);

    if (bad >= 0) {
        fct_fail_at(v, FCT_FAIL, detail, bad, "word");
        return;
    }
    fct_pass(v, "March C- пройдено повністю", (int32_t)RAM_TEST_WORDS, "words");
}
