template <typename LHS, typename RHS>
class VecAdd {
private:
    // Автоматичний вибір: посилання для lvalue, значення для rvalue
    storage_type_t<LHS> lhs_;
    storage_type_t<RHS> rhs_;

public:
    VecAdd(LHS&& lhs, RHS&& rhs)
        : lhs_(std::forward<LHS>(lhs)), rhs_(std::forward<RHS>(rhs)) {}

    double operator[](std::size_t i) const {
        return lhs_[i] + rhs_[i];
    }

    std::size_t size() const {
        return lhs_.size();
    }
};
