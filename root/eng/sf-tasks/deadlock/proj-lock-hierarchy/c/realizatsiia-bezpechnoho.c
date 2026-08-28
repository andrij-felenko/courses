#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <stdint.h>
#include <stdbool.h>

typedef struct {
    uint64_t id;
    int64_t balance;
    pthread_mutex_t mtx;
} account_t;

int account_init(account_t *acc, uint64_t id, int64_t initial_balance) {
    acc->id = id;
    acc->balance = initial_balance;
    return pthread_mutex_init(&acc->mtx, NULL);
}

void account_destroy(account_t *acc) {
    pthread_mutex_destroy(&acc->mtx);
}

// Безпечний переказ коштів між двома рахунками.
// Запобігає дедлоку шляхом упорядкування адрес замків у пам'яті.
bool transfer_money(account_t *from, account_t *to, int64_t amount) {
    if (from == NULL || to == NULL || amount <= 0) {
        return false;
    }

    // Крайовий випадок 1: переказ на той самий рахунок (self-transfer).
    // Спроба повторно захопити неповоротний (non-recursive) м'ютекс
    // тим самим потоком викликає негайний дедлок самого на себе.
    if (from == to) {
        return true; // Сальдо не змінюється
    }

    // Визначаємо глобальний порядок захоплення на основі адрес у пам'яті.
    // Завжди беремо спершу замок із меншою адресою.
    pthread_mutex_t *first_lock;
    pthread_mutex_t *second_lock;

    if ((uintptr_t)&from->mtx < (uintptr_t)&to->mtx) {
        first_lock = &from->mtx;
        second_lock = &to->mtx;
    } else {
        first_lock = &to->mtx;
        second_lock = &from->mtx;
    }

    // Захоплення замків у строгому порядку
    pthread_mutex_lock(first_lock);
    pthread_mutex_lock(second_lock);

    bool success = false;
    if (from->balance >= amount) {
        from->balance -= amount;
        to->balance += amount;
        success = true;
    }

    // Звільнення замків у зворотному порядку
    pthread_mutex_unlock(second_lock);
    pthread_mutex_unlock(first_lock);

    return success;
}
