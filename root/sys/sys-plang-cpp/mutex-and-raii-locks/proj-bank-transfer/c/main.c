#include <pthread.h>
#include <stdio.h>
#include <stdint.h>

typedef struct {
    int id;
    double balance;
    pthread_mutex_t mtx;
} Account;

int transfer_c(Account* from, Account* to, double amount) {
    if (from == to) return 0; // Самоприсвоєння

    // Впорядкування за адресою пам'яті
    Account* first = (uintptr_t)from < (uintptr_t)to ? from : to;
    Account* second = (uintptr_t)from < (uintptr_t)to ? to : from;

    pthread_mutex_lock(&first->mtx);
    pthread_mutex_lock(&second->mtx);

    if (from->balance < amount) {
        pthread_mutex_unlock(&second->mtx);
        pthread_mutex_unlock(&first->mtx);
        return -1; // Недостатньо коштів
    }

    from->balance -= amount;
    to->balance += amount;

    pthread_mutex_unlock(&second->mtx);
    pthread_mutex_unlock(&first->mtx);
    return 1;
}
