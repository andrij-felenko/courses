template <typename Derived>
struct VecExpr {
    // Доступ до елемента за індексом через статичне приведення
    [[nodiscard]] decltype(auto) operator[](std::size_t i) const {
        return static_cast<const Derived&>(*this)[i];
    }

    // Повертає загальну кількість елементів у виразі
    [[nodiscard]] std::size_t size() const {
        return static_cast<const Derived&>(*this).size();
    }
};
