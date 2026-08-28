#include <iostream>

void setup_environment() {
    std::cout << "Global environment setup\n";
}

template <typename T>
void worker_node(T data) {
    setup_environment(); // Незалежне ім'я! Пошук відбувається на Фазі 1.
}

// УВАГА: Функція оголошена ПІСЛЯ визначення шаблону
void setup_environment(int priority) {
    std::cout << "Priority setup: " << priority << "\n";
}
