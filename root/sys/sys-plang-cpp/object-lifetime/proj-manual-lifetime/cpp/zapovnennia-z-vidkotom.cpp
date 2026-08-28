template <class T, std::size_t N>
template <class It>
void StaticVector<T, N>::append(It first, It last) {
    const std::size_t mark = size_;         // позначка: стан «до»
    try {
        for (; first != last; ++first)
            emplace_back(*first);           // може кинути на будь-якій ітерації
    } catch (...) {
        while (size_ != mark) pop_back();   // відкат рівно до позначки
        throw;                              // помилку віддаємо далі незміненою
    }
}
