// calc_v1_v2.cpp — Вихідний код бібліотеки libcalc з підтримкою двох ABI у C++
#include <iostream>
#include <iomanip>

extern "C" {

// 1. Історична реалізація для ABI v1.0
int calc_metric_v1(int items) {
    std::cout << "[libcalc v1.0] Запущено історичний ABI: items = " << items 
              << " (дефолтний scale = 1.0)\n";
    return items * 100;
}
__asm__(".symver calc_metric_v1, calc_metric@LIBCALC_1.0");

// 2. Сучасна реалізація для ABI v2.0
int calc_metric_v2(int items, double scale) {
    std::cout << "[libcalc v2.0] Запущено новий ABI: items = " << items 
              << ", scale = " << std::fixed << std::setprecision(2) << scale << "\n";
    return static_cast<int>(items * 100 * scale);
}
__asm__(".symver calc_metric_v2, calc_metric@@LIBCALC_2.0");

}
