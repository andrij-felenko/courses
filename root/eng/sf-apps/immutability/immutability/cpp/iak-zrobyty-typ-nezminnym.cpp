class Money {
    long cents_;                 // поля приховані — ззовні не дотягтися
    const char* currency_;
public:
    Money(long c, const char* cur) : cents_(c), currency_(cur) {}

    // 1. Жодного методу, що міняє стан. Тільки читання.
    long        cents()    const { return cents_; }
    const char* currency() const { return currency_; }

    // 2. "Зміна" повертає НОВИЙ об'єкт, старий недоторканний.
    Money plus(const Money& o) const {
        return Money(cents_ + o.cents_, currency_);
    }
};

const Money price{ 1999, "UAH" };
Money withTax = price.plus(Money{ 400, "UAH" });  // price лишився 1999
