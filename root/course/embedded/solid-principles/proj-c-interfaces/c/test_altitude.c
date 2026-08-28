// test_altitude.c — хост-тест: компілюється й біжить на ПК, gcc test_altitude.c ...
#include "baro.h"
#include <stdio.h>
#include <math.h>

// ── Політика з основної статті — ТУТ НЕ ЧІПАЄМО, лише використовуємо ──────────
extern float pressure_to_altitude(uint32_t pa);    // барометрична формула, окремо

int altitude_step(baro_t *baro, float *out_m) {
    uint32_t pa;
    baro_status_t err = baro_read(baro, &pa);       // не знає, хто за інтерфейсом
    if (err != BARO_OK) return err;
    *out_m = pressure_to_altitude(pa);
    return BARO_OK;
}

// ── Те, що зшиває політику з БУДЬ-ЯКОЮ реалізацією через спільний інтерфейс ───
static int run_policy(baro_t *b, float *out_m) {
    return altitude_step(b, out_m);     // байдуже, I2C / SPI / мок — той самий виклик
}

// ── Крихітний каркас перевірок (без зовнішніх залежностей) ────────────────────
static int failures = 0;
#define CHECK(cond, msg) do { \
    if (!(cond)) { printf("  FAIL: %s\n", (msg)); failures++; } \
    else         { printf("  ok:   %s\n", (msg)); } } while (0)

#include "baro_mock.c"   // у тесті лінкуємо мок прямо (драйвери шин сюди не йдуть)

int main(void) {
    printf("== сценарій 1: нормальний тиск ==\n");
    {
        // приблизно 95000 Па ≈ 540 м над рівнем моря
        static const baro_step_t s[] = { { BARO_OK, 95000u } };
        baro_mock_t m;
        baro_mock_init(&m, s, 1);
        float h = 0;
        int rc = run_policy(&m.base, &h);            // ← мок як baro_t*
        CHECK(rc == BARO_OK, "політика повернула OK");
        CHECK(fabsf(h - 540.0f) < 30.0f, "висота в очікуваному вікні");
        CHECK(m.calls == 1, "політика читала давач рівно раз");
    }

    printf("== сценарій 2: обрив шини ==\n");
    {
        static const baro_step_t s[] = { { BARO_ERR_BUS, 0u } };
        baro_mock_t m;
        baro_mock_init(&m, s, 1);
        float h = -1.0f;
        int rc = run_policy(&m.base, &h);
        CHECK(rc == BARO_ERR_BUS, "помилка шини проросла нагору без спотворення");
        CHECK(h == -1.0f, "висоту НЕ чіпали при помилці (контракт out_pa)");
    }

    printf("== сценарій 3: абсурдне значення ==\n");
    {
        static const baro_step_t s[] = { { BARO_ERR_RANGE, 0u } };
        baro_mock_t m;
        baro_mock_init(&m, s, 1);
        float h = 0;
        int rc = run_policy(&m.base, &h);
        CHECK(rc == BARO_ERR_RANGE, "вихід за діапазон проріс як окремий код");
    }

    printf("\n%s (%d невдач)\n", failures ? "Є ПРОВАЛИ" : "усе зелено", failures);
    return failures ? 1 : 0;
}
