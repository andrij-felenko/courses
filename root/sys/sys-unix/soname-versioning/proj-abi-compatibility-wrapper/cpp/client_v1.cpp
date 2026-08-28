// client_v1.cpp — Застарілий клієнт C++ (ABI v1.0)
#include <iostream>

extern "C" int calc_metric(int items);

int main() {
    std::cout << "[app_legacy] Викликаємо calc_metric(5)...\n";
    int result = calc_metric(5);
    std::cout << "[app_legacy] Отримано результат: " << result << "\n";
    return 0;
}
