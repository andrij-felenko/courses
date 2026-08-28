#include <functional>
#include <memory>

struct Task {
    std::unique_ptr<int[]> buffer;
};

// Зберігає переміщуваний об'єкт без виділення пам'яті в купі для SBO
std::move_only_function<void() noexcept> task_runner = [t = Task{std::make_unique<int[]>(1024)}]() noexcept {
    // Безпечне виконання задачі
};
