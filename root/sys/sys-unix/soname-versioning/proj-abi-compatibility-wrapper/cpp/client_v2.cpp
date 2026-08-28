// client_v2.cpp — Сучасний клієнт C++ (ABI v2.0)
#include <iostream>

extern "C" int calc_metric(int items, double scale);

int main() {
    std::cout << "[app_modern] Викликаємо calc_metric(5, 1.5)...\n";
    int result = calc_metric(5, 1.5);
    std::cout << "[app_modern] Отримано результат: " << result << "\n";
    return 0;
}
