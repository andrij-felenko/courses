template<typename...>
inline constexpr bool dependent_false = false;

template<typename T>
void handle_valid(T val) {
    if constexpr (std::is_integral_v<T>) {
        // обробка цілих чисел
    } else {
        // ВАЛІДНО: вираз dependent_false<T> залежить від T
        // Компілятор відкладає оцінку на Фазу 2 (інстанціювання)
        static_assert(dependent_false<T>, "Непідтримуваний тип T!");
    }
}
