template <typename Func, typename Tuple, size_t... Is>
constexpr decltype(auto) apply_tuple_impl(Func&& f, Tuple&& t, std::index_sequence<Is...>) {
    return std::forward<Func>(f)(std::get<Is>(std::forward<Tuple>(t))...);
}

template <typename Func, typename Tuple>
constexpr decltype(auto) apply_tuple(Func&& f, Tuple&& t) {
    constexpr size_t size = std::tuple_size_v<std::remove_reference_t<Tuple>>;
    return apply_tuple_impl(
        std::forward<Func>(f),
        std::forward<Tuple>(t),
        std::make_index_sequence<size>{}
    );
}
