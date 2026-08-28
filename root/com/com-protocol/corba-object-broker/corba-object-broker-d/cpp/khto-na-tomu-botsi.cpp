// Сервант — звичайний клас C++, що успадковує згенерований скелет.
class AccountImpl : public POA_bank::Account {
    CORBA::Long balance_;
public:
    explicit AccountImpl(CORBA::Long start) : balance_(start) {}

    CORBA::Long balance() override { return balance_; }

    void withdraw(CORBA::Long amount) override {
        if (amount > balance_) {
            bank::InsufficientFunds e;
            e.shortfall = amount - balance_;
            throw e;                    // помилка з IDL — долетить до клієнта як є
        }
        balance_ -= amount;             // виклик прийшов із пулу потоків ORB:
    }                                   // без блокування тут буде гонитва

    void ping() override {}
};
