#include <stdint.h>
#include <stdbool.h>
#include <time.h>
#include <pthread.h>

#define SNOWFLAKE_EPOCH       1288834974657ULL
#define WORKER_ID_BITS        5
#define DATACENTER_ID_BITS    5
#define SEQUENCE_BITS         12

#define MAX_WORKER_ID         ((1ULL << WORKER_ID_BITS) - 1)
#define MAX_DATACENTER_ID     ((1ULL << DATACENTER_ID_BITS) - 1)
#define SEQUENCE_MASK         ((1ULL << SEQUENCE_BITS) - 1)

#define WORKER_ID_SHIFT       (SEQUENCE_BITS)
#define DATACENTER_ID_SHIFT   (SEQUENCE_BITS + WORKER_ID_BITS)
#define TIMESTAMP_LEFT_SHIFT  (SEQUENCE_BITS + WORKER_ID_BITS + DATACENTER_ID_BITS)

typedef struct {
    uint64_t worker_id;
    uint64_t datacenter_id;
    uint64_t sequence;
    uint64_t last_timestamp;
    pthread_mutex_t lock;
} snowflake_generator_t;

static uint64_t current_time_millis(void) {
    struct timespec ts;
    clock_gettime(CLOCK_REALTIME, &ts);
    return (uint64_t)(ts.tv_sec) * 1000ULL + (uint64_t)(ts.tv_nsec) / 1000000ULL;
}

static uint64_t wait_next_millis(uint64_t last_ts) {
    uint64_t ts = current_time_millis();
    while (ts <= last_ts) {
        ts = current_time_millis();
    }
    return ts;
}

bool snowflake_init(snowflake_generator_t* gen, uint64_t worker_id, uint64_t datacenter_id) {
    if (worker_id > MAX_WORKER_ID || datacenter_id > MAX_DATACENTER_ID) {
        return false;
    }
    gen->worker_id = worker_id;
    gen->datacenter_id = datacenter_id;
    gen->sequence = 0;
    gen->last_timestamp = 0;
    pthread_mutex_init(&gen->lock, NULL);
    return true;
}

bool snowflake_next_id(snowflake_generator_t* gen, uint64_t* out_id) {
    pthread_mutex_lock(&gen->lock);
    uint64_t ts = current_time_millis();

    if (ts < gen->last_timestamp) {
        uint64_t drift = gen->last_timestamp - ts;
        if (drift < 5) {
            ts = wait_next_millis(gen->last_timestamp);
        } else {
            pthread_mutex_unlock(&gen->lock);
            return false; /* Критичний регрес годинника */
        }
    }

    if (ts == gen->last_timestamp) {
        gen->sequence = (gen->sequence + 1) & SEQUENCE_MASK;
        if (gen->sequence == 0) {
            ts = wait_next_millis(gen->last_timestamp);
        }
    } else {
        gen->sequence = 0;
    }

    gen->last_timestamp = ts;

    *out_id = ((ts - SNOWFLAKE_EPOCH) << TIMESTAMP_LEFT_SHIFT)
            | (gen->datacenter_id << DATACENTER_ID_SHIFT)
            | (gen->worker_id << WORKER_ID_SHIFT)
            | gen->sequence;

    pthread_mutex_unlock(&gen->lock);
    return true;
}
