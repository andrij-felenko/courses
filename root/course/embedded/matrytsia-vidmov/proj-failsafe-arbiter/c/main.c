/* Стенд на хост-машині: вичерпна перевірка матриці плюс прогін сценарію
 * у темпі задачі арбітра (50 Гц). Збірка: cc -std=c11 c/*.c -o failsafe */

#include <stdio.h>

#include "failsafe.h"

#define TICK_MS 20u

/* ---------------------------------------------------------------------
 * Еталонна модель: та сама ієрархія, записана вручну ланцюжком if-else.
 * Вона навмисно НЕ використовує таблицю — інакше тест порівнював би код
 * сам із собою. Розбіжність означає, що хтось із двох записів помиляється.
 * ------------------------------------------------------------------- */
static fs_action_t reference_action(uint32_t f)
{
    const bool no_gnss = (f & FS_FAULT_GNSS_GLITCH) != 0u;

    if (f & FS_FAULT_ATTITUDE_LOSS) return FS_ACTION_TERMINATE;
    if (f & FS_FAULT_ACTUATOR)      return FS_ACTION_LAND;
    if (f & FS_FAULT_BATT_CRIT)     return FS_ACTION_LAND;
    if (f & FS_FAULT_GEOFENCE)      return no_gnss ? FS_ACTION_LAND : FS_ACTION_RTL;
    if (f & FS_FAULT_BATT_LOW)      return no_gnss ? FS_ACTION_LAND : FS_ACTION_RTL;
    if (f & FS_FAULT_RC_LOST)       return no_gnss ? FS_ACTION_LAND : FS_ACTION_RTL;
    if (no_gnss)                    return FS_ACTION_ALTHOLD;
    if (f & FS_FAULT_GCS_LOST)      return FS_ACTION_WARN;
    return FS_ACTION_NONE;
}

static void print_mask(uint32_t mask)
{
    if (mask == 0u) {
        printf("норма");
        return;
    }
    for (unsigned i = 0; i < FS_FAULT_COUNT; ++i) {
        if (mask & (1u << i)) {
            printf("%s ", fs_fault_name(i));
        }
    }
}

/* Усі 256 комбінацій восьмибітної маски. Фільтрацію вимикаємо нулями
 * порогів: тут перевіряється ієрархія, а не таймери. */
static int check_matrix(void)
{
    fs_config_t cfg = fs_config_default();
    for (unsigned i = 0; i < FS_FAULT_COUNT; ++i) {
        cfg.debounce_ms[i] = 0u;
    }
    cfg.action_hold_ms = 0u;

    int failed = 0;
    for (uint32_t mask = 0; mask <= FS_FAULT_ALL; ++mask) {
        fs_state_t st;
        fs_arbiter_init(&st, &cfg);
        fs_arbiter_preflight_done(&st, 0u);

        const fs_action_t got = fs_arbiter_update(&st, mask, TICK_MS);
        const fs_action_t expected = reference_action(mask);
        if (got != expected) {
            printf("  0x%02X: таблиця дала %s, еталон %s | ",
                   mask, fs_action_name(got), fs_action_name(expected));
            print_mask(mask);
            printf("\n");
            ++failed;
        }
    }
    printf("Матриця: перевірено %u комбінацій, розбіжностей %d\n",
           FS_FAULT_ALL + 1u, failed);
    return failed;
}

/* ---------------------------------------------------------------------
 * Сценарій драйверів. У прошивці кожен рядок — окремий обробник
 * переривання, що смикає свій біт; тут події просто розкладені по осі часу.
 * ------------------------------------------------------------------- */
static void drivers_tick(fs_inbox_t *box, uint32_t t)
{
    /* GNSS ловить сузір'я перші 200 мс — це не відмова, це старт */
    fs_report_fault(box, FS_FAULT_GNSS_GLITCH, t < 200u);
    /* Провал радіоканалу 400–600 мс фільтр з'їдає; з 1000 до 4000 — справжня втрата */
    fs_report_fault(box, FS_FAULT_RC_LOST,
                    (t >= 400u && t < 600u) || (t >= 1000u && t < 4000u));
    /* Просадка напруги на маневрі 3000–3200 мс і справжній розряд із 6000 */
    fs_report_fault(box, FS_FAULT_BATT_LOW,
                    (t >= 3000u && t < 3200u) || t >= 6000u);
    fs_report_fault(box, FS_FAULT_BATT_CRIT, t >= 8000u);
    fs_report_fault(box, FS_FAULT_ATTITUDE_LOSS, t >= 10000u);
}

static void run_timeline(void)
{
    fs_inbox_t inbox;
    fs_state_t st;
    const fs_config_t cfg = fs_config_default();

    fs_inbox_init(&inbox);
    fs_arbiter_init(&st, &cfg);

    fs_action_t last = FS_ACTION_NONE;
    printf("Час, мс | дія | підтверджені відмови\n");

    for (uint32_t t = 0; t <= 10400u; t += TICK_MS) {
        drivers_tick(&inbox, t);

        /* Калібрування завершене — з цієї миті таймери мають сенс */
        if (t == 200u) {
            fs_arbiter_preflight_done(&st, t);
            printf("%7u | преполіт завершено, арбітр увімкнено\n", t);
        }
        /* Оператор побачив на пульті RTL і повернув собі керування */
        if (t == 5000u) {
            const bool ok = fs_arbiter_operator_ack(&st, t);
            printf("%7u | команда оператора: скидання фіксації → %s\n",
                   t, ok ? "прийнято" : "відхилено");
            last = fs_arbiter_action(&st);
        }

        const uint32_t raw = fs_inbox_snapshot(&inbox);
        const fs_action_t action = fs_arbiter_update(&st, raw, t);

        if (action != last) {
            printf("%7u | %-9s | ", t, fs_action_name(action));
            print_mask(fs_arbiter_confirmed(&st));
            printf("\n");
            last = action;
        }
    }

    /* Після посадки й зняття з охорони фіксація знімається повністю */
    fs_arbiter_disarm(&st);
    printf("  disarm → %s\n", fs_action_name(fs_arbiter_action(&st)));
}

int main(void)
{
    const int failed = check_matrix();
    printf("\n");
    run_timeline();
    return failed == 0 ? 0 : 1;
}
