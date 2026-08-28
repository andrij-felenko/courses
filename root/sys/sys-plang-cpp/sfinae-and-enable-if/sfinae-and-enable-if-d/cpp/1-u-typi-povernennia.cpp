// Активується тільки для цілих типів (int, short, long тощо)
template<typename T>
std::enable_if_t<std::is_integral_v<T>, void>
process(T val) {
    std::cout << "Обробка цілого числа: " << val << "\n";
}

// Активується тільки для чисел із плаваючою крапкою (float, double)
template<typename T>
std::enable_if_t<std::is_floating_point_v<T>, void>
process(T val) {
    std::cout << "Обробка дійсного числа: " << val << "\n";
}
