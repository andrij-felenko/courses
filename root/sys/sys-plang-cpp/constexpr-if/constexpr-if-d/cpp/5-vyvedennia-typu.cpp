#include <type_traits>
#include <string>

template<typename T>
auto get_representation(T val) {
    if constexpr (std::is_integral_v<T>) {
        return static_cast<long long>(val); // Для цілих повертає long long
    } else if constexpr (std::is_floating_point_v<T>) {
        return static_cast<double>(val);    // Для дійсних повертає double
    } else {
        return std::string(val);            // Для решти повертає рядок
    }
}
