#include <stdint.h>
#include <stdbool.h>
#include <pthread.h>

typedef struct {
    int64_t balance;
    pthread_mutex_t lock;
} SafeAccount;

void safe_account_init(SafeAccount *acc, int64_t initial_balance) {
    acc->balance = initial_balance;
    pthread_mutex_init(&acc->lock, NULL);
}

void safe_account_destroy(SafeAccount *acc) {
    pthread_mutex_destroy(&acc->lock);
}

void safe_account_deposit(SafeAccount *acc, int64_t amount) {
    pthread_mutex_lock(&acc->lock);
    acc->balance += amount;
    pthread_mutex_unlock(&acc->lock);
}

bool safe_account_withdraw(SafeAccount *acc, int64_t amount) {
    pthread_mutex_lock(&acc->lock);
    if (acc->balance >= amount) {
        acc->balance -= amount;
        pthread_mutex_unlock(&acc->lock);
        return true;
    }
    pthread_mutex_unlock(&acc->lock);
    return false;
}
