#include <stdio.h>
#include "dt838_analyzer.h"

static void print_diode_test(float voltage_mv) {
    dt838_diode_result_t res = dt838_analyze_diode(voltage_mv);
    printf("  [Вхід: %6.1f мВ] -> %-45s (Тип: %d)\n", 
           res.voltage_drop_mv, res.description, res.type);
}

static void print_continuity_test(float ohm) {
    dt838_continuity_result_t res = dt838_analyze_continuity(ohm);
    printf("  [Опір: %8.1f Ом] -> Стан: %d | Зумер: %s\n",
           res.resistance_ohm, res.state, res.beeper_active ? "ВВІМКНЕНО (BEEP!)" : "ВИМКНЕНО");
}

static void print_hfe_test(float ic_ua) {
    dt838_hfe_result_t res = dt838_calculate_hfe(ic_ua);
    if (res.valid) {
        printf("  [Ic: %7.1f мкА] -> hFE = %5.1f (Валідно)\n", res.collector_current_ua, res.hfe_gain);
    } else {
        printf("  [Ic: %7.1f мкА] -> Перевантаження / недійсне значення hFE\n", res.collector_current_ua);
    }
}

int main(void) {
    printf("=====================================================\n");
    printf(" Демонстрація аналізатора вимірювань мультиметра DT-838\n");
    printf("=====================================================\n\n");

    printf("1. Тестування p-n переходів (Режим діодної прозвонки):\n");
    print_diode_test(15.0f);     /* Коротке замикання */
    print_diode_test(250.0f);    /* Германієвий діод */
    print_diode_test(650.0f);    /* Кремнієвий p-n перехід */
    print_diode_test(2100.0f);   /* Червоний світлодіод */
    print_diode_test(3200.0f);   /* Обрив / зворотний напрямок */
    printf("\n");

    printf("2. Перевірка цілісності кола (Звуковий зумер та опір):\n");
    print_continuity_test(4.7f);     /* Перемичка (BEEP!) */
    print_continuity_test(47.0f);    /* Низький опір (BEEP!) */
    print_continuity_test(150.0f);   /* Опір без звуку */
    print_continuity_test(5000000.0f);/* Оверлоад / Обрив */
    printf("\n");

    printf("3. Обчислення коефіцієнта підсилення hFE вбудованої колодки:\n");
    print_hfe_test(1500.0f);   /* Ic = 1500 мкА -> hFE = 150 */
    print_hfe_test(3500.0f);   /* Ic = 3500 мкА -> hFE = 350 */
    print_hfe_test(12000.0f);  /* Ic = 12000 мкА -> hFE > 1000 (Оверлоад) */
    printf("\n");

    return 0;
}
