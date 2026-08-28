template<typename T>
void validate(T x) {
    // ВАЛІДНО: константний предикат метаінформації про тип
    if constexpr (std::is_integral_v<T>) { /* ... */ }

    // ВАЛІДНО: вираз оператора sizeof є константою компіляції
    if constexpr (sizeof(T) > 8) { /* ... */ }

    // ПОМИЛКА: значення параметра x відоме лише у runtime!
    if constexpr (x > 0) { /* ... */ } 
}
