// main.cpp — точка входу та використання інтерфейсу (C++)
#include <iostream>
#include <memory>
#include "engine.hpp"

int main() {
    std::unique_ptr<IFilter> filter = std::make_unique<GainFilter>(5);

    // Віртуальний виклик через vtable
    std::int32_t step1 = filter->process(10);

    // Виклик функції з іншого модуля
    std::int32_t step2 = fast_scale(step1, 3);

    std::cout << "Result: " << step2 << "\n";
    return 0;
}
