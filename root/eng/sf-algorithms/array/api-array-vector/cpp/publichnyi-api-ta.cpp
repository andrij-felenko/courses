#include <span>
#include <vector>
#include <array>
#include <iostream>

// Функція приймає зріз будь-якого неперервного масиву
void process_elements(std::span<const int> s) {
    std::cout << "Розмір зрізу: " << s.size() << " елементів\n";
    for (int val : s) {
        std::cout << val << " ";
    }
    std::cout << "\n";
}

int main() {
    int raw_arr[4] = {1, 2, 3, 4};
    std::array<int, 4> std_arr = {10, 20, 30, 40};
    std::vector<int> vec = {100, 200, 300, 400};

    // span уніфікує виклики без копіювання даних та без виділення пам'яті
    process_elements(raw_arr);
    process_elements(std_arr);
    process_elements(vec);

    // Створення підзрізу (subspan)
    process_elements(vec.size() > 2 ? std::span<const int>(vec).subspan(1, 2) : std::span<const int>());
}
