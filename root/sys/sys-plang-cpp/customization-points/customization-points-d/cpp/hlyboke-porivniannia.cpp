// C++14 SFINAE підхід (громіздкий і важкий для компілятора)
template<typename T>
auto draw_helper(T&& t, int)
    -> decltype(std::forward<T>(t).draw(), void()) {
    std::forward<T>(t).draw();
}

template<typename T>
void draw_helper(T&& t, long) {
    // Фолбек
}
