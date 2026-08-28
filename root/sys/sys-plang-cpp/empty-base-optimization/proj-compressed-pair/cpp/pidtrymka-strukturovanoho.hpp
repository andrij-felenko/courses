namespace modern {

template <size_t Index, typename T1, typename T2>
constexpr decltype(auto) get(compressed_pair<T1, T2>& p) noexcept {
    if constexpr (Index == 0) return p.first();
    else if constexpr (Index == 1) return p.second();
}

template <size_t Index, typename T1, typename T2>
constexpr decltype(auto) get(const compressed_pair<T1, T2>& p) noexcept {
    if constexpr (Index == 0) return p.first();
    else if constexpr (Index == 1) return p.second();
}

template <size_t Index, typename T1, typename T2>
constexpr decltype(auto) get(compressed_pair<T1, T2>&& p) noexcept {
    if constexpr (Index == 0) return std::move(p.first());
    else if constexpr (Index == 1) return std::move(p.second());
}

} // namespace modern

// Спеціалізації в просторі імен std
namespace std {

template <typename T1, typename T2>
struct tuple_size<modern::compressed_pair<T1, T2>>
    : std::integral_constant<size_t, 2> {};

template <typename T1, typename T2>
struct tuple_element<0, modern::compressed_pair<T1, T2>> {
    using type = T1;
};

template <typename T1, typename T2>
struct tuple_element<1, modern::compressed_pair<T1, T2>> {
    using type = T2;
};

} // namespace std
