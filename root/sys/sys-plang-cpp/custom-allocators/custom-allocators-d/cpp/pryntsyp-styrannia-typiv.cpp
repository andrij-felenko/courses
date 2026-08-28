#include <vector>
#include <memory_resource>
#include <array>
#include <iostream>

void populate_data(std::pmr::vector<int>& vec) {
    for (int i = 0; i < 100; ++i) {
        vec.push_back(i * 2);
    }
}

void run_example() {
    // 1. Вектор на швидкому локальному буфері в стеку
    std::array<std::byte, 1024> stack_buffer;
    std::pmr::monotonic_buffer_resource stack_arena(stack_buffer.data(), stack_buffer.size());
    std::pmr::vector<int> stack_vec(&stack_arena);

    // 2. Вектор на системній купі
    std::pmr::vector<int> heap_vec(std::pmr::new_delete_resource());

    populate_data(stack_vec); // Працює без системних викликів malloc
    populate_data(heap_vec);  // Працює з купою — обидва вектори повністю сумісні!
}
