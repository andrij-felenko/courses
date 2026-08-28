template <typename T>
concept VectorExpression = requires(const T& expr, std::size_t i) {
    { expr.size() } -> std::convertible_to<std::size_t>;
    { expr[i] }     -> std::convertible_to<double>;
};

// Простий і чистий оператор додавання без CRTP і без SFINAE
template <VectorExpression LHS, VectorExpression RHS>
auto operator+(const LHS& lhs, const RHS& rhs) {
    return VecAdd<LHS, RHS>(lhs, rhs);
}
