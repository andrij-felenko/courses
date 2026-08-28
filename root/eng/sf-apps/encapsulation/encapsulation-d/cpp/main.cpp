class Account {
    long balance = 0;            // private за замовчуванням у class — приховане
public:
    void deposit(long sum) {
        if (sum <= 0) throw std::invalid_argument("сума має бути додатною");
        balance += sum;
    }
    void withdraw(long sum) {
        if (sum <= 0) throw std::invalid_argument("сума має бути додатною");
        if (sum > balance) throw std::runtime_error("недостатньо коштів");  // інваріант
        balance -= sum;
    }
    long amount() const { return balance; }   // лише читання
};
