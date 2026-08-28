template <typename>
inline constexpr bool dependent_false_v = false;

template <typename T>
void dispatch_operation(T val) {
    if constexpr (std::is_integral_v<T>) {
        process_integer(val);
    } else if constexpr (std::is_floating_point_v<T>) {
        process_floating(val);
    } else {
        static_assert(dependent_false_v<T>, "Тип не підтримується для dispatch_operation!");
    }
}
