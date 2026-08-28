class Vector : public VecExpr<Vector> {
private:
    std::vector<double> data_;

public:
    explicit Vector(std::size_t size, double val = 0.0) : data_(size, val) {}

    // Конструктор ініціалізації з довільного виразу
    template <typename E>
    Vector(const VecExpr<E>& expr) : data_(expr.size()) {
        *this = expr;
    }

    // Оператор присвоєння — ДРАЙВЕР ОБЧИСЛЕННЯ ВЕСЬОГО ДЕРЕВА
    template <typename E>
    Vector& operator=(const VecExpr<E>& expr) {
        const E& e = static_cast<const E&>(expr);
        const std::size_t n = e.size();
        
        if (data_.size() != n) {
            data_.resize(n);
        }
        
        // Єдиний цикл усього виразу!
        for (std::size_t i = 0; i < n; ++i) {
            data_[i] = e[i];
        }
        return *this;
    }

    double operator[](std::size_t i) const { return data_[i]; }
    double& operator[](std::size_t i) { return data_[i]; }
    std::size_t size() const { return data_.size(); }
};
