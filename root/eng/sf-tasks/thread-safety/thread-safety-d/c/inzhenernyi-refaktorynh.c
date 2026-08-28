#include <pthread.h>
#include <stdint.h>
#include <stdbool.h>

typedef struct {
    pthread_mutex_t lock;
    uint64_t total_requests;
    uint64_t total_errors;
} RequestAggregator;

int aggregator_init(RequestAggregator *agg) {
    if (!agg) return -1;
    agg->total_requests = 0;
    agg->total_errors = 0;
    return pthread_mutex_init(&agg->lock, NULL);
}

void aggregator_record(RequestAggregator *agg, bool is_error) {
    if (!agg) return;
    pthread_mutex_lock(&agg->lock);
    agg->total_requests++;
    if (is_error) {
        agg->total_errors++;
    }
    pthread_mutex_unlock(&agg->lock);
}

void aggregator_read_snapshot(RequestAggregator *agg, uint64_t *out_req, uint64_t *out_err) {
    if (!agg) return;
    pthread_mutex_lock(&agg->lock);
    if (out_req) *out_req = agg->total_requests;
    if (out_err) *out_err = agg->total_errors;
    pthread_mutex_unlock(&agg->lock);
}

void aggregator_destroy(RequestAggregator *agg) {
    if (agg) {
        pthread_mutex_destroy(&agg->lock);
    }
}
