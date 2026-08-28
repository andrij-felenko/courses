#include <pthread.h>
#include <stdio.h>
#include <stdbool.h>

typedef struct {
    pthread_mutex_t lock;
    int data;
} SafeContainer;

void init_container(SafeContainer* c) {
    pthread_mutex_init(&c->lock, NULL);
    c->data = 0;
}

void write_data(SafeContainer* c, int val) {
    pthread_mutex_lock(&c->lock);
    c->data = val;
    pthread_mutex_unlock(&c->lock);
}

void destroy_container(SafeContainer* c) {
    pthread_mutex_destroy(&c->lock);
}
