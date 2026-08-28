#include <pthread.h>
#include <stdint.h>

typedef struct {
    pthread_mutex_t lock;
    uint64_t total_bytes;
    uint64_t error_count;
} ThreadSafeMetrics;

int metrics_init(ThreadSafeMetrics *m) {
    if (m == NULL) return -1;
    m->total_bytes = 0;
    m->error_count = 0;
    return pthread_mutex_init(&m->lock, NULL);
}

void metrics_record(ThreadSafeMetrics *m, int status_code, uint64_t bytes) {
    if (m == NULL) return;

    pthread_mutex_lock(&m->lock);
    m->total_bytes += bytes;
    if (status_code >= 400) {
        m->error_count++;
    }
    pthread_mutex_unlock(&m->lock);
}

void metrics_get_snapshot(ThreadSafeMetrics *m, uint64_t *out_bytes, uint64_t *out_errors) {
    if (m == NULL) return;

    pthread_mutex_lock(&m->lock);
    if (out_bytes != NULL) *out_bytes = m->total_bytes;
    if (out_errors != NULL) *out_errors = m->error_count;
    pthread_mutex_unlock(&m->lock);
}

void metrics_destroy(ThreadSafeMetrics *m) {
    if (m != NULL) {
        pthread_mutex_destroy(&m->lock);
    }
}
