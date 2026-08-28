#include <iostream>

// Базовий випадок зупинки рекурсії розгортання
void log_all() {
    std::cout << "\n";
}

// Рекурсивний крок: перший аргумент відокремлюється, решта розгортається
template<typename First, typename... Rest>
void log_all(const First& first, const Rest&... rest) {
    std::cout << first << " ";
    log_all(rest...); // Рекурсивний виклик для залишку пакета
}
