template <typename Op, typename E>
class VecUnary : public VecExpr<VecUnary<Op, E>> {
private:
    const E& expr_;
    Op op_;

public:
    VecUnary(const E& expr, Op op = Op{}) : expr_(expr), op_(op) {}

    double operator[](std::size_t i) const {
        return op_(expr_[i]);
    }

    std::size_t size() const {
        return expr_.size();
    }
};
