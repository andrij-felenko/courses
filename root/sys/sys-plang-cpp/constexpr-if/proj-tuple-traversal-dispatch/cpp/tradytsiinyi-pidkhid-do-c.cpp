// Традиційний підхід C++11/C++14: розрив логіки на два окремі шаблони
template<std::size_t Index, std::size_t Size>
struct TupleIterator {
    template<typename Tuple, typename Func>
    static void iterate(const Tuple& t, Func&& f) {
        f(std::get<Index>(t), Index);
        // Рекурсивний виклик для наступного індексу
        TupleIterator<Index + 1, Size>::iterate(t, std::forward<Func>(f));
    }
};

// Часткова спеціалізація для зупинки рекурсії, коли Index == Size
template<std::size_t Size>
struct TupleIterator<Size, Size> {
    template<typename Tuple, typename Func>
    static void iterate(const Tuple&, Func&&) {
        // Базовий випадок: нічого не робимо
    }
};
