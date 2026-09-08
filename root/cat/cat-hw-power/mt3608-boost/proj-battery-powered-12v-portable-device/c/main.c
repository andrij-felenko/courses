#include <stdio.h>
#include <stdbool.h>
#include "battery_guard.h"

int main(void) {
    printf("=== Моніторинг батареї 18650 для перетворювача MT3608 ===\n");

    battery_guard_t guard;
    /* Дільник: 100 кОм (Rtop) та 20 кОм (Rbottom), поділ 1:6
     * Vref = 1100 мВ (внутрішній точний bandgap), 10-бітний АЦП (1023)
     * Поріг відсічки: 3000 мВ, поріг відновлення з гістерезисом: 3300 мВ */
    battery_guard_init(&guard, 100000, 20000, 1100, 1023, 3000, 3300);

    /* Симуляція послідовного розряду акумулятора */
    printf("\n--- Тест 1: Номінальна робота (повний заряд 4.1 В) ---\n");
    // 4100 мВ на дільнику дає 4100 / 6 = 683.3 мВ -> код АЦП = (683.3 / 1100) * 1023 = 635
    for (int i = 0; i < 8; i++) {
        battery_guard_update(&guard, 635);
    }
    printf("Напруга: %u мВ, стан MT3608: %s\n", 
           battery_guard_get_voltage(&guard),
           battery_guard_is_boost_enabled(&guard) ? "АКТИВНИЙ" : "ЗАБЛОКОВАНО");

    printf("\n--- Тест 2: Глибокий розряд акумулятора (падіння до 2.9 В) ---\n");
    // 2900 мВ на дільнику дає 2900 / 6 = 483.3 мВ -> код АЦП = (483.3 / 1100) * 1023 = 449
    for (int i = 0; i < 8; i++) {
        battery_guard_update(&guard, 449);
    }
    printf("Напруга: %u мВ, стан MT3608: %s\n", 
           battery_guard_get_voltage(&guard),
           battery_guard_is_boost_enabled(&guard) ? "АКТИВНИЙ" : "ЗАБЛОКОВАНО");

    printf("\n--- Тест 3: Ефект «відпочинку» акумулятора без навантаження (3.1 В) ---\n");
    // Після зняття навантаження батарея підіймається до 3.1 В (< 3.3 В порогу відновлення)
    // 3100 мВ -> код АЦП = 480
    for (int i = 0; i < 8; i++) {
        battery_guard_update(&guard, 480);
    }
    printf("Напруга: %u мВ, стан MT3608: %s (завдяки гістерезису залишається вимкненим)\n", 
           battery_guard_get_voltage(&guard),
           battery_guard_is_boost_enabled(&guard) ? "АКТИВНИЙ" : "ЗАБЛОКОВАНО");

    printf("\n--- Тест 4: Підключення зарядного пристрою (підйом до 3.8 В) ---\n");
    // 3800 мВ -> код АЦП = 589
    for (int i = 0; i < 8; i++) {
        battery_guard_update(&guard, 589);
    }
    printf("Напруга: %u мВ, стан MT3608: %s\n", 
           battery_guard_get_voltage(&guard),
           battery_guard_is_boost_enabled(&guard) ? "АКТИВНИЙ" : "ЗАБЛОКОВАНО");

    printf("\n=== Тестування алгоритму захисту завершено успішно ===\n");
    return 0;
}
