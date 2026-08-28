template<typename T>
void process_value(T val) {
    if constexpr (std::is_integral_v<T>) {
        std::cout << "Ціле число\n";
    } else if constexpr (std::is_floating_point_v<T>) {
        std::cout << "Дійсне число\n";
    } else {
        static_assert(sizeof(T) == 0, "Непідтримуваний тип даних!");
    }
}
