template<typename T>
void process_data(T val) {
    if constexpr (std::is_integral_v<T>) {
        // обробка цілих чисел
    } else if constexpr (std::is_floating_point_v<T>) {
        // обробка дійсних чисел
    } else {
        // ПОМИЛКА КОМПІЛЯЦІЇ У C++17/C++20!
        static_assert(false, "Тип даних не підтримується процесором!");
    }
}
