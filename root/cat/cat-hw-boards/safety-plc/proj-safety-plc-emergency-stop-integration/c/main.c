#include <stdio.h>
#include <stdbool.h>
#include <stdint.h>
#include "safety_plc.h"

/**
 * @file main.c
 * @brief Точка входу в програму Safety PLC: ініціалізація, детермінований головний цикл,
 *        тестове фазове зондування входів, обробка безпекової логіки та симуляція аварійних ситуацій.
 */

static void print_plc_status(const safety_plc_t *plc, const char *step_name) {
    printf("\n=== [%s] ===\n", step_name);
    printf("Стан автомата: %s\n", safety_state_to_string(plc->state));
    printf("Глобальні помилки: 0x%04X (%s)\n", plc->global_faults, safety_fault_to_string(plc->global_faults));
    printf("Тестові виходи: T1=%d, T2=%d (Фаза %d)\n", plc->t1_generator, plc->t2_generator, plc->current_phase);
    
    for (uint8_t i = 0; i < SAFETY_DI_COUNT; i++) {
        printf("  [F-DI_%d] Raw: A=%d B=%d | Filtered: A=%d B=%d | History: A=0x%02X B=0x%02X | SafeVal=%d | Faults=0x%04X\n",
               i, plc->di[i].raw_a, plc->di[i].raw_b,
               plc->di[i].filtered_a, plc->di[i].filtered_b,
               plc->di[i].history_a, plc->di[i].history_b,
               plc->di[i].safe_value, plc->di[i].faults);
    }
    
    for (uint8_t i = 0; i < SAFETY_DO_COUNT; i++) {
        printf("  [F-DO_%d] Cmd=%d | Keys: HighSide=%d LowSide=%d | Readback: HS=%d LS=%d EDM=%d | Faults=0x%04X\n",
               i, plc->do_out[i].command,
               plc->do_out[i].hs_output, plc->do_out[i].ls_output,
               plc->do_out[i].hs_readback, plc->do_out[i].ls_readback,
               plc->do_out[i].edm_feedback, plc->do_out[i].faults);
    }
}

int main(void) {
    safety_plc_t plc;

    printf("===============================================================\n");
    printf("  ПРОГРАМОВАНИЙ ЛОГІЧНИЙ КОНТРОЛЕР БЕЗПЕКИ (SAFETY PLC SIL3)  \n");
    printf("===============================================================\n");

    /* 1. Ініціалізація підсистеми функціональної безпеки */
    safety_plc_init(&plc);
    print_plc_status(&plc, "1. Після ініціалізації");

    /* 2. Симуляція детермінованого циклу у нормальному режимі (E-Stop віджатий, лінії здорові) */
    printf("\n--- 2. Симуляція штатної роботи (E-Stop OK, 10 циклів) ---\n");
    for (int cycle = 0; cycle < 10; cycle++) {
        /* Крок 1: виконання тактів контролера (генерація T1/T2) */
        safety_plc_process_step(&plc, 10);

        /* Крок 2: подача здорового фазового відгуку від замкненої кнопки Аварійної Зупинки (E-Stop) */
        /* Канал A живиться від T1, Канал B живиться від T2 */
        bool raw_a = plc.t1_generator;
        bool raw_b = plc.t2_generator;

        for (uint8_t di_idx = 0; di_idx < SAFETY_DI_COUNT; di_idx++) {
            safety_plc_read_f_di(&plc, di_idx, raw_a, raw_b);
            safety_plc_evaluate_f_di_diagnostics(&plc, di_idx, 10);
        }

        /* Крок 3: Вирішення логіки безпеки (силові виходи вмикаються при валідному F-DI) */
        bool safety_logic_demand = plc.di[0].safe_value && plc.di[1].safe_value;

        /* Крок 4: Оновлення виходів F-DO з подачею коректного зворотного зв'язку */
        for (uint8_t do_idx = 0; do_idx < SAFETY_DO_COUNT; do_idx++) {
            bool expected_hs = safety_logic_demand;
            bool expected_ls = safety_logic_demand;
            bool expected_edm = !safety_logic_demand; /* NC-контакт розмикається при ввімкненні реле */

            safety_plc_update_f_do(&plc, do_idx, safety_logic_demand, expected_hs, expected_ls, expected_edm, 10);
        }
    }
    print_plc_status(&plc, "2. Нормальний робочий режим (F-DO Активні)");

    /* 3. ТЕСТ 1: Впровадження короткого замикання лінії F-DI на VCC (+24V) */
    printf("\n---------------------------------------------------------------\n");
    printf("  ТЕСТ 1: Впровадження короткого замикання F-DI_0 ChA на VCC (+24V)\n");
    printf("---------------------------------------------------------------\n");
    
    /* Зміна фази */
    safety_plc_process_step(&plc, 10);
    /* На Фазі 1 (коли T1 = 0) примусово падає 1 через коротке замикання на VCC */
    safety_plc_read_f_di(&plc, 0, true, plc.t2_generator);
    safety_plc_evaluate_f_di_diagnostics(&plc, 0, 10);

    /* Оновлення F-DO в аварійному стані */
    safety_plc_update_f_do(&plc, 0, false, false, false, true, 10);
    print_plc_status(&plc, "3. Реакція на Short to VCC (Автомат у FAIL-SAFE)");

    /* 4. ТЕСТ 2: Спроба скидання помилки при активному короткому замиканні */
    printf("\n--- 4. Спроба скидання (RESET) при збережній несправності ---\n");
    bool reset_ok = safety_plc_reset_faults(&plc, true);
    printf("Результат виконання RESET: %s\n", reset_ok ? "УСПІШНО" : "ВІДХИЛЕНО (Помилка залишається)");

    /* 5. ТЕСТ 3: Усунення короткого замикання та відновлення системи */
    printf("\n--- 5. Усунення замикання на VCC та повторний RESET ---\n");
    plc.di[0].faults = SAFETY_FAULT_NONE; /* Фізичне усунення пошкодження кабелю */
    reset_ok = safety_plc_reset_faults(&plc, true);
    printf("Результат виконання RESET після ремонту: %s\n", reset_ok ? "УСПІШНО (Повернення в RUN)" : "ВІДХИЛЕНО");
    print_plc_status(&plc, "5. Після успішного скидання помилок");

    /* 6. ТЕСТ 4: Перехресне коротке замикання між каналами A та B (Cross-Fault) */
    printf("\n---------------------------------------------------------------\n");
    printf("  ТЕСТ 4: Впровадження перехресного замикання між лініями A та B  \n");
    printf("---------------------------------------------------------------\n");
    safety_plc_process_step(&plc, 10);
    /* Замикання між проводами: імпульс з T1 затікає в обидва канали одночасно */
    safety_plc_read_f_di(&plc, 0, true, true);
    safety_plc_evaluate_f_di_diagnostics(&plc, 0, 10);
    print_plc_status(&plc, "6. Реакція на Cross-Fault (Перехресне замикання)");

    /* Очищення після тесту 4 */
    plc.di[0].faults = SAFETY_FAULT_NONE;
    safety_plc_reset_faults(&plc, true);

    /* 7. ТЕСТ 5: Таймаут часової розбіжності (Discrepancy Timeout) */
    printf("\n---------------------------------------------------------------\n");
    printf("  ТЕСТ 5: Імітація залипання одного контакту кнопки E-Stop (Discrepancy)\n");
    printf("---------------------------------------------------------------\n");
    
    /* Імітуємо, що контакт A замкнено, а контакт B зламано і розімкнено */
    for (int ms = 0; ms < 60; ms += 10) {
        safety_plc_process_step(&plc, 10);
        /* Надаємо валідні імпульсите лише каналу A, а канал B залишаємо у 0 */
        bool raw_a = plc.t1_generator;
        bool raw_b = false;
        
        safety_plc_read_f_di(&plc, 0, raw_a, raw_b);
        safety_plc_evaluate_f_di_diagnostics(&plc, 0, 10);
        
        if (plc.state == SAFETY_STATE_FAILSAFE) {
            printf("Fail-Safe спрацював на %d мс тривалості розбіжності!\n", ms + 10);
            break;
        }
    }
    print_plc_status(&plc, "7. Спрацьовування таймауту розбіжності входів (50 мс)");

    /* Очищення після тесту 5 */
    plc.di[0].faults = SAFETY_FAULT_NONE;
    plc.di[0].history_a = 0;
    plc.di[0].history_b = 0;
    safety_plc_reset_faults(&plc, true);

    /* 8. ТЕСТ 6: Несправність зворотного зв'язку EDM F-DO (Зварено контактор) */
    printf("\n---------------------------------------------------------------\n");
    printf("  ТЕСТ 6: Імітація зварювання контактів зовнішнього реле (EDM fault)\n");
    printf("---------------------------------------------------------------\n");
    
    /* Увімкнення виходу F-DO, але EDM не змінює стан (NC контакт заклинило у розімкненому/замкненому стані) */
    for (int ms = 0; ms < 120; ms += 20) {
        /* Вважаємо, що логіка вимагає увімкнення, але EDM повертає неправильне значення (true замість false) */
        safety_plc_update_f_do(&plc, 0, true, true, true, true, 20);
        if (plc.state == SAFETY_STATE_FAILSAFE) {
            printf("Fail-Safe спрацював на %d мс таймауту EDM!\n", ms + 20);
            break;
        }
    }
    print_plc_status(&plc, "8. Реакція на аномалію EDM контактора (Fail-Safe)");

    printf("\n===============================================================\n");
    printf("  ДЕМОНСТРАЦІЮ РОБОТИ ДРАЙВЕРА SAFETY PLC УСПІШНО ЗАВЕРШЕНО   \n");
    printf("===============================================================\n");

    return 0;
}
