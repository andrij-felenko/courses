template <typename LHS, typename RHS>
class VecAdd : public VecExpr<VecAdd<LHS, RHS>> {
private:
    const LHS& lhs_;
    const RHS& rhs_;

public:
    VecAdd(const LHS& lhs, const RHS& rhs) : lhs_(lhs), rhs_(rhs) {}

    // Метод доступу обчислює суму для i-го елемента «льоту»
    double operator[](std::size_t i) const {
        return lhs_[i] + rhs_[i];
    }

    std::size_t size() const {
        return lhs_.size();
    }
};
