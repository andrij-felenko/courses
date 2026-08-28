// Підхід C++14/C++17: обмеження через SFINAE у списку параметрів за замовчуванням
template<typename T, 
         typename = std::enable_if_t<std::is_integral_v<T>>>
void process_value(T value) {
    // Реалізація для цілих чисел
}

template<typename T, 
         typename = std::enable_if_t<std::is_floating_point_v<T>>,
         typename = void> // Штучний параметр для уникнення однакових сигнатур шаблону
void process_value(T value) {
    // Реалізація для чисел із плаваючою комою
}
