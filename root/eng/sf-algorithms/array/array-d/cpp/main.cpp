#include <iostream>
#include <vector>
#include <array>
#include <span>

void print_span(std::span<const int> view) {
    std::cout << "Елементи через span: ";
    for (int val : view) {
        std::cout << val << " ";
    }
    std::cout << "\n";
}

int main() {
    // 1. Статичний безпечний масив (на стеку)
    std::array<int, 5> static_arr = {10, 20, 30, 40, 50};
    std::cout << "std::array A[2] = " << static_arr.at(2) << "\n";

    // 2. Динамічний вектор (у купі)
    std::vector<int> dyn_vec;
    dyn_vec.reserve(4); // Заздалегідь резервуємо пам'ять

    for (int i = 0; i < 10; ++i) {
        dyn_vec.push_back((i + 1) * 100);
    }

    std::cout << "std::vector: розмір = " << dyn_vec.size() 
              << ", місткість = " << dyn_vec.capacity() << "\n";

    // 3. Неволодіючий зріз (C++20 span)
    print_span(static_arr);
    print_span(dyn_vec);

    return 0;
}
