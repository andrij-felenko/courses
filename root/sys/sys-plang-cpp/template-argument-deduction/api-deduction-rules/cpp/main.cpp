// std::pair (C++17)
template<class T1, class T2>
pair(T1, T2) -> pair<T1, T2>;

// std::array (C++17)
template<class T, class... U>
array(T, U...) -> array<T, 1 + sizeof...(U)>;

// std::span (C++20)
template<class It, class EndOrSize>
span(It, EndOrSize) -> span<std::remove_reference_t<std::iter_reference_t<It>>>;

template<class T, std::size_t N>
span(T (&)[N]) -> span<T, N>;
