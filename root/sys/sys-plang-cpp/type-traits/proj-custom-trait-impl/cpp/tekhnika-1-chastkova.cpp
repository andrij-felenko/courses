#include <iostream>
#include <type_traits>
#include <vector>
#include <string>

// 1. Первинний шаблон: за замовчуванням будь-який тип — це не std::vector
template<typename T>
struct is_std_vector : std::false_type {};

// 2. Часткова спеціалізація для будь-якого std::vector<T, Alloc>
template<typename T, typename Alloc>
struct is_std_vector<std::vector<T, Alloc>> : std::true_type {};

// 3. Змінна-допомагач (C++17 variable template)
template<typename T>
inline constexpr bool is_std_vector_v = is_std_vector<T>::value;

int main() {
    std::cout << std::boolalpha;
    std::cout << "int є vector: " << is_std_vector_v<int> << "\n"; // false
    std::cout << "std::vector<double> є vector: " 
              << is_std_vector_v<std::vector<double>> << "\n"; // true
}
