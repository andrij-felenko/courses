// Допоміжний шаблон залежної константи
template<typename...>
inline constexpr bool dependent_false = false;

template<typename T>
void process_data_safe(T val) {
    if constexpr (std::is_integral_v<T>) {
        // обробка цілих чисел
    } else if constexpr (std::is_floating_point_v<T>) {
        // обробка дійсних чисел
    } else {
        // ВАЛІДНО: dependent_false<T> оцінюється лише під час інстанціювання гілки else
        static_assert(dependent_false<T>, "Тип даних не підтримується процесором!");
    }
}
