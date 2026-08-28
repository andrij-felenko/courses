// C++: Ідіоматичне непряме сортування через std::vector<size_t> та std::sort
#include <iostream>
#include <vector>
#include <string>
#include <algorithm>
#include <numeric>

struct LargeTask {
    int id;
    int priority;
    std::string payload;
};

std::vector<size_t> create_indirect_stable_permutation(const std::vector<LargeTask>& tasks) {
    std::vector<size_t> indices(tasks.size());
    std::iota(indices.begin(), indices.end(), 0); // Заповнюємо 0, 1, 2, ..., n-1

    std::sort(indices.begin(), indices.end(), [&tasks](size_t a, size_t b) {
        if (tasks[a].priority != tasks[b].priority) {
            return tasks[a].priority > tasks[b].priority; // Спадіння
        }
        return a < b; // Стійке порівняння початкових індексів
    });

    return indices;
}

int main() {
    std::vector<LargeTask> tasks = {
        {101, 3, "Завдання 1"},
        {102, 5, "Завдання 2 (перше з пріоритетом 5)"},
        {103, 3, "Завдання 3"},
        {104, 5, "Завдання 4 (друге з пріоритетом 5)"}
    };

    auto perm = create_indirect_stable_permutation(tasks);

    std::cout << "=== Результат непрямого стійкого сортування ===\n";
    for (size_t idx : perm) {
        std::cout << "  Task ID: " << tasks[idx].id
                  << " | Priority: " << tasks[idx].priority
                  << " | Payload: " << tasks[idx].payload << "\n";
    }

    return 0;
}
