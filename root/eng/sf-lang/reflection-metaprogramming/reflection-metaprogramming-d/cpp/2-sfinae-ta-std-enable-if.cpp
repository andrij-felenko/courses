#include <type_traits>
#include <iostream>

// Перевантаження 1: лише для цілих чисел
template <typename T>
typename std::enable_if<std::is_integral<T>::value, void>::type
process(T value) {
    std::cout << "Цілочисельна обробка: " << value << '\n';
}

// Перевантаження 2: лише для чисел із рухомою комою
template <typename T>
typename std::enable_if<std::is_floating_point<T>::value, void>::type
process(T value) {
    std::cout << "Обробка числа з рухомою комою: " << value << '\n';
}
