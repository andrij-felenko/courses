template <typename T>
auto serialize_value(const T& val) {
    if constexpr (std::is_arithmetic_v<T>) {
        return std::to_string(val);
    } else if constexpr (std::is_same_v<T, std::string>) {
        return "\"" + val + "\"";
    } else {
        // Відкинута гілка навіть не вимагає валідності операцій для невідповідного типу
        return val.custom_to_json();
    }
}
