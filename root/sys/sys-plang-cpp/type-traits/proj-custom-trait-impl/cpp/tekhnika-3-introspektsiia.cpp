#include <iostream>
#include <type_traits>
#include <vector>
#include <iterator>

template<typename T, typename = void>
struct is_iterable : std::false_type {};

template<typename T>
struct is_iterable<T, std::void_t<
    decltype(std::begin(std::declval<T&>())),
    decltype(std::end(std::declval<T&>()))
>> : std::true_type {};

template<typename T>
inline constexpr bool is_iterable_v = is_iterable<T>::value;

int main() {
    std::cout << std::boolalpha;
    std::cout << "vector є iterable: " << is_iterable_v<std::vector<int>> << "\n"; // true
    std::cout << "int[5] є iterable: " << is_iterable_v<int[5]> << "\n";           // true
    std::cout << "double є iterable: " << is_iterable_v<double> << "\n";           // false
}
