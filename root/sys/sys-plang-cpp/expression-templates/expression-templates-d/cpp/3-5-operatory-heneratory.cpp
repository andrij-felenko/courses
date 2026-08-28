template <typename LHS, typename RHS>
VecAdd<LHS, RHS> operator+(const VecExpr<LHS>& lhs, const VecExpr<RHS>& rhs) {
    return VecAdd<LHS, RHS>(
        static_cast<const LHS&>(lhs),
        static_cast<const RHS&>(rhs)
    );
}

template <typename E>
VecScale<E> operator*(const VecExpr<E>& expr, double alpha) {
    return VecScale<E>(static_cast<const E&>(expr), alpha);
}

template <typename E>
VecScale<E> operator*(double alpha, const VecExpr<E>& expr) {
    return VecScale<E>(static_cast<const E&>(expr), alpha);
}
