#include <stdint.h>
#include <stdbool.h>
#include <time.h>
#include <pthread.h>

#define RING_BUF_SIZE 256

typedef struct {
    char topic[96];
    char payload[160];
    time_t timestamp;
} telemetry_entry_t;

typedef struct {
    telemetry_entry_t entries[RING_BUF_SIZE];
    size_t head;
    size_t tail;
    size_t count;
    pthread_mutex_t lock;
} threadsafe_ring_t;

void ring_init(threadsafe_ring_t *r) {
    r->head = 0;
    r->tail = 0;
    r->count = 0;
    pthread_mutex_init(&r->lock, NULL);
}

/* Додавання з витісненням найстарішого запису (FIFO Drop) */
void ring_push_overwrite(threadsafe_ring_t *r, const telemetry_entry_t *item) {
    pthread_mutex_lock(&r->lock);
    if (r->count == RING_BUF_SIZE) {
        /* Буфер повний: пересуваємо tail, звільняючи найстаріший елемент */
        r->tail = (r->tail + 1) % RING_BUF_SIZE;
        r->count--;
    }
    r->entries[r->head] = *item;
    r->head = (r->head + 1) % RING_BUF_SIZE;
    r->count++;
    pthread_mutex_unlock(&r->lock);
}
