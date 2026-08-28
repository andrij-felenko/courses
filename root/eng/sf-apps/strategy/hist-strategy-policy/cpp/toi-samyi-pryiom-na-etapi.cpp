// (1) КЛАСИЧНА стратегія: поведінка — рантайм-ОБ'ЄКТ за вказівником/посиланням.
//     Який алгоритм — вирішується під час РОБОТИ програми.
struct DiscountPolicy {
    virtual double discount(double total) const = 0;   // спільний інтерфейс
    virtual ~DiscountPolicy() = default;
};
struct VipDiscount : DiscountPolicy {
    double discount(double total) const override { return total * 0.20; }
};

struct Order {
    DiscountPolicy* policy;                             // поле — підставна поведінка
    double total;
    double final_price() const {
        return total - policy->discount(total);         // віртуальний виклик у рантаймі
    }
};
