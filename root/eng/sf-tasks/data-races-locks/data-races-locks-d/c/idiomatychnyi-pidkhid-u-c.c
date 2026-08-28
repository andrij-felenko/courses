#include <pthread.h>
#include <stdbool.h>

typedef struct {
    int value;
    pthread_mutex_t lock;
} Counter;

// У мові C використовують явне ручне звільнення або структурований вихід goto cleanup
bool counter_add_safe(Counter *c, int delta) {
    pthread_mutex_lock(&c->lock);
    
    if (delta < 0 && c->value < -delta) {
        pthread_mutex_unlock(&c->lock); // Ручне звільнення перед виходом
        return false;
    }
    
    c->value += delta;
    pthread_mutex_unlock(&c->lock);
    return true;
}
