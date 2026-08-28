#include <stdio.h>
#include <stdbool.h>
#include <stddef.h>

typedef struct {
    int id;
    double balance;
    bool is_active;
} Account;

// Імперативна мутація стану масиву за місцем
void apply_monthly_fee(Account* accounts, size_t count, double fee) {
    for (size_t i = 0; i < count; ++i) {
        // Керування потоком і зміна стану комірки пам'яті
        if (accounts[i].is_active && accounts[i].balance >= fee) {
            accounts[i].balance -= fee; // Побічний ефект: мутація пам'яті
        } else if (accounts[i].is_active) {
            accounts[i].is_active = false; // Зміна інваріанту активності
        }
    }
}
