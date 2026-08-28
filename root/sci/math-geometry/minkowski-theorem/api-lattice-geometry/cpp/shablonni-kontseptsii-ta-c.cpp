namespace latgeom {

template<typename T>
concept LatticeScalar = std::is_integral_v<T> || std::is_floating_point_v<T>;

template<typename M>
concept LatticeMatrix = requires(M m, size_t i, size_t j) {
    { m(i, j) } -> std::convertible_to<double>;
    { m.rows() } -> std::same_as<size_t>;
    { m.cols() } -> std::same_as<size_t>;
};

} // namespace latgeom
