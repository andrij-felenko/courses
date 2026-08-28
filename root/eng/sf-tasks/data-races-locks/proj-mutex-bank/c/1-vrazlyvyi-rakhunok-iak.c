#include <stdint.h>
#include <stdbool.h>

typedef struct {
    int64_t balance;
} UnsafeAccount;

void account_deposit_unsafe(UnsafeAccount *acc, int64_t amount) {
    acc->balance += amount; // ПЕРЕГОНИ ДАНИХ (Load -> Add -> Store)
}

bool account_withdraw_unsafe(UnsafeAccount *acc, int64_t amount) {
    if (acc->balance >= amount) {
        acc->balance -= amount; // ПЕРЕГОНИ ДАНИХ (Check-Then-Act)
        return true;
    }
    return false;
}
