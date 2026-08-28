// calc_v1_v2.c — Вихідний код бібліотеки libcalc з підтримкою двох ABI у C
#include <stdio.h>

// 1. Історична реалізація для ABI v1.0
// Ця функція обробляє виклики від бінарних файлів, скомпільованих під LIBCALC_1.0
int calc_metric_v1(int items) {
    printf("[libcalc v1.0] Запущено історичний ABI: items = %d (дефолтний scale = 1.0)\n", items);
    return items * 100;
}
// Прив'язуємо внутрішнє ім'я calc_metric_v1 до символу calc_metric@LIBCALC_1.0 (один собачка)
__asm__(".symver calc_metric_v1, calc_metric@LIBCALC_1.0");

// 2. Сучасна реалізація для ABI v2.0
// Ця функція приймає додатковий параметр з плаваючою крапкою
int calc_metric_v2(int items, double scale) {
    printf("[libcalc v2.0] Запущено новий ABI: items = %d, scale = %.2f\n", items, scale);
    return (int)(items * 100 * scale);
}
// Прив'язуємо внутрішнє ім'я calc_metric_v2 до дефолтного символу calc_metric@@LIBCALC_2.0 (два собачки)
__asm__(".symver calc_metric_v2, calc_metric@@LIBCALC_2.0");
