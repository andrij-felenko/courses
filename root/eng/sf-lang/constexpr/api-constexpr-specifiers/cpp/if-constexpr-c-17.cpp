#include <type_traits>
#include <vector>

template <typename T>
auto extract_element(const T& container) {
    if constexpr (std::is_pointer_v<T>) {
        return *container;          // Інстанціюється, лише якщо T — вказівник
    } else if constexpr (requires { container.front(); }) {
        return container.front();   // Інстанціюється для контейнерів із методом front()
    } else {
        return container;           // Інстанціюється для скалярних значень
    }
}
