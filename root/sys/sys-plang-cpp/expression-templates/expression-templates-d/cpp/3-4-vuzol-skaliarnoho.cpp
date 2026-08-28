template <typename E>
class VecScale : public VecExpr<VecScale<E>> {
private:
    const E& expr_;
    double alpha_;

public:
    VecScale(const E& expr, double alpha) : expr_(expr), alpha_(alpha) {}

    double operator[](std::size_t i) const {
        return expr_[i] * alpha_;
    }

    std::size_t size() const {
        return expr_.size();
    }
};
