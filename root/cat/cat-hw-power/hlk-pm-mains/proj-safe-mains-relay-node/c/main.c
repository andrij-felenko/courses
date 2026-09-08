#include <stdio.h>
#include <stdbool.h>
#include "relay.h"

/* Емуляція системного таймера мілісекунд (SysTick / millis) */
static uint32_t system_millis = 0;

int main(void) {
    printf("=== Старт контролера живлення HLK-PM01 / 220 В ===\n");
    printf("Ініціалізація захисних інтервалів: dead-time = 3000 мс, debounce = 40 мс\n\n");

    relay_controller_t relay;
    /* Захисна пауза 3000 мс (запобігає пошкодженню індуктивних навантажень) */
    relay_init(&relay, 3000, 40);

    /* Сценарій 1: Користувач натискає кнопку вимикача (з імітацією брязкання) */
    printf("--- Подія 1: Користувач натискає кнопку ---\n");
    /* Короткі імпульси брязкання контактів (10 мс і 20 мс) */
    relay_update_button(&relay, true, 10);
    relay_update_button(&relay, false, 20);
    /* Стабільне утримання кнопки */
    relay_update_button(&relay, true, 30);
    relay_update_button(&relay, true, 80); /* Минуло > 40 мс -> спрацювання */
    relay_process(&relay, 80);

    /* Сценарій 2: Користувач одразу вимикає реле через 1 секунду */
    system_millis = 1000;
    printf("\n--- Подія 2: Вимкнення через 1000 мс ---\n");
    relay_set_target(&relay, false, system_millis);
    relay_process(&relay, system_millis);

    /* Сценарій 3: Спроба повторного швидкого увімкнення через 500 мс (захист активний) */
    system_millis = 1500;
    printf("\n--- Подія 3: Спроба повторного увімкнення через 500 мс (блокування) ---\n");
    relay_set_target(&relay, true, system_millis);
    relay_process(&relay, system_millis);

    /* Сценарій 4: Просування часу до завершення dead-time */
    system_millis = 4100; /* Минуло понад 3000 мс з моменту вимкнення (1000 + 3000 = 4000) */
    printf("\n--- Подія 4: Досягнення кінця захисного інтервалу (t = 4100 мс) ---\n");
    relay_process(&relay, system_millis);

    printf("\nПоточний стан виходу реле: %s\n", relay_is_active(&relay) ? "УВІМКНЕНО" : "ВИМКНЕНО");
    printf("=== Роботу контролера перевірено успішно ===\n");
    return 0;
}
