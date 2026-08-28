#include <iostream>
#include <sstream>
#include <random>
#include <cassert>

void test_stream_serialization() {
    std::mt19937 rng1(12345);
    for (int i = 0; i < 100; ++i) rng1(); // Зміщуємо стан

    // Збереження стану генератора у текстовий потік
    std::stringstream ss;
    ss << rng1;

    // Відновлення стану у новому об'єкті
    std::mt19937 rng2;
    ss >> rng2;

    // Обидва генератори видають тотожні числа
    assert(rng1() == rng2());
    std::cout << "✔ Потокова серіалізація стану виконана успішно!\n";
}
