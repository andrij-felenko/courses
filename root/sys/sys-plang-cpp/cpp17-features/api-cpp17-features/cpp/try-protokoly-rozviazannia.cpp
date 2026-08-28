// Повна реалізація користувацького Tuple-подібного протоколу:
struct Coordinate2D {
    double latitude;
    double longitude;
};

template <>
struct std::tuple_size<Coordinate2D> : std::integral_constant<std::size_t, 2> {};

template <std::size_t I>
struct std::tuple_element<I, Coordinate2D> {
    using type = double;
};

template <std::size_t I>
decltype(auto) get(const Coordinate2D& c) noexcept {
    if constexpr (I == 0) return c.latitude;
    else if constexpr (I == 1) return c.longitude;
}
