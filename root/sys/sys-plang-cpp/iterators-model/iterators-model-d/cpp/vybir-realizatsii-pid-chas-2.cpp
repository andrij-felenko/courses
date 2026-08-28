template<typename It, typename Distance>
void advance(It& it, Distance n) {
    using category = typename std::iterator_traits<It>::iterator_category;

    if constexpr (std::is_base_of_v<std::random_access_iterator_tag, category>) {
        it += n; // Оптимізована гілка за O(1)
    } else {
        while (n > 0) { ++it; --n; } // Покроковий прохід за O(n)
    }
}
