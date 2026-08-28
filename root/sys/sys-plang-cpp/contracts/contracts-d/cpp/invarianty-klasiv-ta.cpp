class BankAccount {
private:
    int id_{0};
    int balance_{0};

    [[nodiscard]] bool check_class_invariant() const noexcept {
        return id_ > 0 && balance_ >= 0;
    }

public:
    explicit BankAccount(int id, int initial_deposit) noexcept
        pre [valid_id]: id > 0
        pre [valid_deposit]: initial_deposit >= 0
        post: check_class_invariant()
        : id_(id), balance_(initial_deposit) {}

    void deposit(int amount) noexcept
        pre: check_class_invariant()
        pre [positive_amount]: amount > 0
        post: check_class_invariant()
    {
        balance_ += amount;
    }

    void withdraw(int amount) noexcept
        pre: check_class_invariant()
        pre [sufficient_funds]: amount > 0 && amount <= balance_
        post: check_class_invariant()
    {
        balance_ -= amount;
    }

    [[nodiscard]] int balance() const noexcept
        pre: check_class_invariant()
        post(b): b == balance_ && check_class_invariant()
    {
        return balance_;
    }
};
