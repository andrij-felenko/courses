class Account {
    long cents_ = 0;
public:
    // «const» = обіцянка: це ЗАПИТ, об'єкт не зміниться
    long balance() const {
        // cents_ = 0;   // ← не скомпілюється: порушення обіцянки
        return cents_;
    }
    // без «const» — це КОМАНДА, їй міняти стан вільно
    void withdraw(long amount) {
        cents_ -= amount;
    }
};
