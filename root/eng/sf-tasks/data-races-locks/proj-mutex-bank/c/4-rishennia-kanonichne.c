#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <pthread.h>

bool safe_account_transfer(SafeAccount *from, SafeAccount *to, int64_t amount) {
    if (from == to || amount <= 0) {
        return false;
    }

    // Визначаємо канонічний порядок блокування за адресою в пам'яті
    SafeAccount *first = from;
    SafeAccount *second = to;
    if ((uintptr_t)from > (uintptr_t)to) {
        first = to;
        second = from;
    }

    // Захоплюємо замки у строго визначеному порядку: менша адреса -> більша адреса
    pthread_mutex_lock(&first->lock);
    pthread_mutex_lock(&second->lock);

    bool success = false;
    if (from->balance >= amount) {
        from->balance -= amount;
        to->balance += amount;
        success = true;
    }

    // Звільняємо у зворотному порядку
    pthread_mutex_unlock(&second->lock);
    pthread_mutex_unlock(&first->lock);

    return success;
}
