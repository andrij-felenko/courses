// Таблиця steps[] — та сама; різниця лише в тому, куди йде звіт.
// printf тут заведений на huart2 (ST-Link VCP) через _write().
void configure_module(void) {
    char resp[64];
    for (size_t i = 0; i < sizeof(steps) / sizeof(steps[0]); i++) {
        bool ok = send_at(steps[i].cmd, resp, sizeof(resp), 1000);
        printf("%s  →  %s", steps[i].what, resp);          // повний текст відповіді
        if (!ok) {
            printf(">>> НЕ OK. Перевір: EN високо? швидкість 38400? \\r\\n?\n");
            return;                                        // далі немає сенсу
        }
    }
    printf("Налаштування завершено. Знеструм і подай живлення без EN.\n");
}
