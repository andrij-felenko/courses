template<typename T>
auto extract_data(T obj) {
    if constexpr (std::is_pointer_v<T>) {
        return *obj;          // Якщо T = double*, результуючий тип: double
    } else if constexpr (std::is_integral_v<T>) {
        return obj * 2;        // Якщо T = int, результуючий тип: int
    } else {
        return std::string(obj); // Якщо T = const char*, результуючий тип: std::string
    }
}
