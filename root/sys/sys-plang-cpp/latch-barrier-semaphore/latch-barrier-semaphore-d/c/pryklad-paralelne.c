#include <stdio.h>
#include <pthread.h>
#include <unistd.h>

/* В аналогічній POSIX C реалізації доводиться створювати м'ютекс,
   умовну змінну та вручну контролювати цілочисельний лічильник */
typedef struct {
    pthread_mutex_t mtx;
    pthread_cond_t cv;
    int counter;
} posix_latch_t;

void posix_latch_init(posix_latch_t* l, int count) {
    pthread_mutex_init(&l->mtx, NULL);
    pthread_cond_init(&l->cv, NULL);
    l->counter = count;
}

void posix_latch_count_down(posix_latch_t* l) {
    pthread_mutex_lock(&l->mtx);
    l->counter--;
    if (l->counter == 0) {
        pthread_cond_broadcast(&l->cv);
    }
    pthread_mutex_unlock(&l->mtx);
}

void posix_latch_wait(posix_latch_t* l) {
    pthread_mutex_lock(&l->mtx);
    while (l->counter > 0) {
        pthread_cond_wait(&l->cv, &l->mtx);
    }
    pthread_mutex_unlock(&l->mtx);
}

void posix_latch_destroy(posix_latch_t* l) {
    pthread_mutex_destroy(&l->mtx);
    pthread_cond_destroy(&l->cv);
}
