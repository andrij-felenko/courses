// Приклад скидання та керування WDT у тривалому циклі (C / Non-OS SDK)
#include "c_types.h"
#include "osapi.h"
#include "user_interface.h"

void execute_heavy_computation(void) {
    uint32_t i;
    os_printf("Початок тривалих обчислень...\n");

    for (i = 0; i < 20000; i++) {
        // Проведення обчислювальної операції
        os_delay_us(150);

        // Періодичне скидання WDT кожні 5000 ітерацій (~0.75 с)
        if (i % 5000 == 0) {
            system_soft_wdt_feed();
            os_printf("WDT скинуто на ітерації: %u\n", i);
        }
    }

    os_printf("Обчислення успішно завершено!\n");
}
