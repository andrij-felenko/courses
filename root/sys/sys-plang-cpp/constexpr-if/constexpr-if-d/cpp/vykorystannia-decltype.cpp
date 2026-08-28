template<typename T>
decltype(auto) access_element(T& container) {
    if constexpr (std::is_pointer_v<T>) {
        return *container; // Повертає lvalue-посилання на розіменований об'єкт
    } else if constexpr (requires { container.front(); }) {
        return container.front(); // Повертає посилання на перший елемент
    } else {
        return container; // Повертає посилання на сам контейнер
    }
}
