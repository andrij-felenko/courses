#include <iostream>
#include <iterator>
#include <vector>

// Шаблонний клас динамічного буфера
template <typename T>
class Buffer {
public:
    template <typename Iter>
    Buffer(Iter begin, Iter end) {
        // Завантаження елементів з ітераторів
    }
};

// Явна напрямна дедукції (Deduction Guide):
// Підказуємо компілятору, що тип T буфера є типом елемента, на який вказує ітератор Iter
template <typename Iter>
Buffer(Iter, Iter) -> Buffer<typename std::iterator_traits<Iter>::value_type>;

int main() {
    std::vector<int> numbers = {10, 20, 30};
    
    // Завдяки напрямній компілятор самостійно виводить Buffer<int>
    Buffer buf(numbers.begin(), numbers.end());
    return 0;
}
