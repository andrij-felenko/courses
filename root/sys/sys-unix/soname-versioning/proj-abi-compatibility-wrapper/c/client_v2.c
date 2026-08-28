// client_v2.c — Сучасний клієнт C (ABI v2.0)
#include <stdio.h>

// Оголошення оновленої сигнатури функції
extern int calc_metric(int items, double scale);

int main(void) {
    printf("[app_modern] Викликаємо calc_metric(5, 1.5)...\n");
    int result = calc_metric(5, 1.5);
    printf("[app_modern] Отримано результат: %d\n", result);
    return 0;
}
