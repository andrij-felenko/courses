template <typename LHS, typename RHS>
class MixedVecAdd {
public:
    // Тип результату визначається як спільний тип операндів
    using value_type = std::common_type_t<
        typename LHS::value_type,
        typename RHS::value_type
    >;

private:
    const LHS& lhs_;
    const RHS& rhs_;

public:
    MixedVecAdd(const LHS& lhs, const RHS& rhs) : lhs_(lhs), rhs_(rhs) {}

    value_type operator[](std::size_t i) const {
        return static_cast<value_type>(lhs_[i]) + static_cast<value_type>(rhs_[i]);
    }

    std::size_t size() const { return lhs_.size(); }
};
