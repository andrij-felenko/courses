#include <stdint.h>
#include <stdbool.h>
#include <pthread.h>

typedef struct {
    int64_t balance;
    pthread_mutex_t lock;
} Account;

bool transfer_c(Account *from, Account *to, int64_t amount) {
    // Впорядковуємо захоплення за фізичною адресою в пам'яті для уникнення дедлоку
    Account *first = from;
    Account *second = to;
    if ((uintptr_t)from > (uintptr_t)to) {
        first = to;
        second = from;
    }

    pthread_mutex_lock(&first->lock);
    pthread_mutex_lock(&second->lock);

    bool success = false;
    if (from->balance >= amount) {
        from->balance -= amount;
        to->balance += amount;
        success = true;
    }

    pthread_mutex_unlock(&second->lock);
    pthread_mutex_unlock(&first->lock);
    return success;
}
