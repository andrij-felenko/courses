// client_v1.c — Застарілий клієнт C (ABI v1.0)
#include <stdio.h>

// Оголошення першої сигнатури функції
extern int calc_metric(int items);

int main(void) {
    printf("[app_legacy] Викликаємо calc_metric(5)...\n");
    int result = calc_metric(5);
    printf("[app_legacy] Отримано результат: %d\n", result);
    return 0;
}
