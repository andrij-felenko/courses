#include <pthread.h>
#include <stdint.h>
#include <stdbool.h>

typedef struct {
    int value;
    pthread_mutex_t mtx;
} node_t;

// БЕЗПЕЧНО: замки захоплюються в єдиному глобальному порядку за адресою в пам'яті
void swap_nodes_safe(node_t *a, node_t *b) {
    if (a == NULL || b == NULL || a == b) {
        return; // Захист від самоблокування (self-deadlock)
    }

    pthread_mutex_t *first = &a->mtx;
    pthread_mutex_t *second = &b->mtx;

    // Впорядкування адрес: ліквідація циклічного очікування
    if ((uintptr_t)first > (uintptr_t)second) {
        first = &b->mtx;
        second = &a->mtx;
    }

    pthread_mutex_lock(first);
    pthread_mutex_lock(second);

    int temp = a->value;
    a->value = b->value;
    b->value = temp;

    pthread_mutex_unlock(second);
    pthread_mutex_unlock(first);
}
