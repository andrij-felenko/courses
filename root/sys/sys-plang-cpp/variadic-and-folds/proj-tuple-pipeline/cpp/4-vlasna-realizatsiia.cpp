namespace custom {

template <typename Func, typename Tuple, size_t... Indices>
constexpr decltype(auto) apply_impl(Func&& func, Tuple&& tuple, std::index_sequence<Indices...>) {
    // Розпакування пакету індексів у патерн std::get<Indices>
    return std::forward<Func>(func)(
        std::get<Indices>(std::forward<Tuple>(tuple))...
    );
}

template <typename Func, typename Tuple>
constexpr decltype(auto) apply(Func&& func, Tuple&& tuple) {
    constexpr size_t tuple_size = std::tuple_size_v<std::remove_reference_t<Tuple>>;
    return apply_impl(
        std::forward<Func>(func),
        std::forward<Tuple>(tuple),
        std::make_index_sequence<tuple_size>{}
    );
}

} // namespace custom
