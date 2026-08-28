#include <functional>
#include <iostream>
#include <vector>

// Приклад використання std::function_ref у C++26 для виклику зворотного зв'язку
void filter_numbers(const std::vector<int>& numbers, std::function_ref<bool(int)> predicate) {
    for (int n : numbers) {
        if (predicate(n)) {
            std::cout << n << ' ';
        }
    }
    std::cout << '\n';
}

int main() {
    std::vector<int> data = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10};

    int threshold = 5;
    // Лямбда передається без жодної алокації та без копіювання буфера!
    filter_numbers(data, [threshold](int val) { return val > threshold; });
}
