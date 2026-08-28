template <typename Derived>
class ExpressionBase {
public:
    // Примусова оцінка виразу у тимчасовий конкретний контейнер
    template <typename ConcreteContainer>
    [[nodiscard]] ConcreteContainer eval() const {
        ConcreteContainer temp(static_cast<const Derived&>(*this).size());
        temp = static_cast<const Derived&>(*this); // Викликає злитий цикл
        return temp;
    }
};
