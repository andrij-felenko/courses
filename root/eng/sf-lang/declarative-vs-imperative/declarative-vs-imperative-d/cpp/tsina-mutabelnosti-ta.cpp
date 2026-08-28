#include <cstddef>
#include <span>

struct Account {
    int id;
    double balance;
    bool is_active;
};

// Імперативна функція: покрокова зміна мутабельних об'єктів
void apply_monthly_fee(std::span<Account> accounts, double fee) {
    for (auto& account : accounts) {
        if (account.is_active && account.balance >= fee) {
            account.balance -= fee;
        } else if (account.is_active) {
            account.is_active = false;
        }
    }
}
