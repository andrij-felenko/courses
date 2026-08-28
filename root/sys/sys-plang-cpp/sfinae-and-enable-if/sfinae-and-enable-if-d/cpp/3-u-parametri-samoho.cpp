// ПРАВИЛЬНИЙ СИСТЕМНИЙ ПІДХІД
template<typename T,
         std::enable_if_t<std::is_integral_v<T>, int> = 0>
void print_value(T val) {
    std::cout << "Integral: " << val << "\n";
}

template<typename T,
         std::enable_if_t<std::is_floating_point_v<T>, int> = 0>
void print_value(T val) {
    std::cout << "Floating: " << val << "\n";
}
