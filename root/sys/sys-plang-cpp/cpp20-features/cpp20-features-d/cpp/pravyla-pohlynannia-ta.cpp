template<std::input_iterator I>
void advance_cursor(I& it, std::size_t n) {
    // Лінійне переміщення O(N) для звичайного ітератора
    while (n--) ++it;
}

template<std::random_access_iterator I>
void advance_cursor(I& it, std::size_t n) {
    // Миттєвий перехід O(1) для ітератора довільного доступу
    it += n;
}
