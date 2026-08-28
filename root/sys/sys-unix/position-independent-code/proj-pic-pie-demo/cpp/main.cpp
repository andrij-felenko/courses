// main.cpp — C++-версія головного виконуваного файлу
#include <iostream>

extern "C" {
    extern int global_counter;
    extern void exported_func(const char* msg);
}

int main() {
    std::cout << "[main cpp] Початкове значення: " << global_counter << "\n";
    exported_func("Виклик з C++ main");
    std::cout << "[main cpp] Кінцеве значення: " << global_counter << "\n";
    return 0;
}
