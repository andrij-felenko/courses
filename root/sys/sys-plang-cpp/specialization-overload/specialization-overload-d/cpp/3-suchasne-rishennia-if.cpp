template<typename T>
void process_modern(const T& val) {
    if constexpr (std::is_pointer_v<T>) {
        if (val != nullptr) {
            process_modern(*val);
        }
    } 
    else if constexpr (std::is_integral_v<T>) {
        // Оптимізований шлях для цілих чисел
    } 
    else {
        // Загальний шлях
    }
}
