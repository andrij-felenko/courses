#include <functional>
#include <memory>
#include <iostream>

// C++23: Move-only лямбда із захопленням унікального покажчика
std::move_only_function<void()> create_task() {
    auto data = std::make_unique<int>(42);
    return [d = std::move(data)]() {
        std::cout << "Task executed with value: " << *d << '\n';
    };
}
