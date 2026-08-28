#include <iostream>

void dce_examples(int a, int b) noexcept {
    // Випадок 1: Синтаксично недосяжний блок (гарантовано видаляється)
    return;
    [[maybe_unused]] int dead_val = a + b;

    // Випадок 2: Семантично недосяжний блок через складний інваріант
    if (a * a + b * b < 0) {
        std::cout << "Цей рядок ніколи не виконається!\n";
    }
}
