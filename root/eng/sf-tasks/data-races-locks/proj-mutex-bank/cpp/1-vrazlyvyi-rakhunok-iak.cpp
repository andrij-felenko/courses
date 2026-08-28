#include <cstdint>

struct UnsafeAccount {
    int64_t balance{0};

    void deposit(int64_t amount) noexcept {
        balance += amount; // ПЕРЕГОНИ ДАНИХ (неподільна на вигляд, але три кроки в CPU)
    }

    bool withdraw(int64_t amount) noexcept {
        if (balance >= amount) {
            balance -= amount; // ПЕРЕГОНИ ДАНИХ (між перевіркою і відніманням втручається інший потік)
            return true;
        }
        return false;
    }
};
