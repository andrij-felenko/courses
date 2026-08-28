#include <errno.h>
#include <pthread.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

typedef struct {
    pthread_rwlock_t rwlock;
    char             key[64];
    char             value[256];
} registry_entry_t;

void registry_init(registry_entry_t *reg) {
    pthread_rwlock_init(&reg->rwlock, NULL);
    strcpy(reg->key, "status");
    strcpy(reg->value, "active");
}

bool registry_read(registry_entry_t *reg, char *out_buf, size_t max_len) {
    if (pthread_rwlock_rdlock(&reg->rwlock) != 0) {
        return false;
    }
    strncpy(out_buf, reg->value, max_len - 1);
    out_buf[max_len - 1] = '\0';
    pthread_rwlock_unlock(&reg->rwlock);
    return true;
}

bool registry_read_timed(registry_entry_t *reg, char *out_buf, size_t max_len, int timeout_ms) {
    struct timespec ts;
    clock_gettime(CLOCK_REALTIME, &ts);
    ts.tv_sec += timeout_ms / 1000;
    ts.tv_nsec += (timeout_ms % 1000) * 1000000;
    if (ts.tv_nsec >= 1000000000) {
        ts.tv_sec += 1;
        ts.tv_nsec -= 1000000000;
    }

    int rc = pthread_rwlock_timedrdlock(&reg->rwlock, &ts);
    if (rc == ETIMEDOUT) {
        return false;
    }
    if (rc != 0) {
        return false;
    }

    strncpy(out_buf, reg->value, max_len - 1);
    out_buf[max_len - 1] = '\0';
    pthread_rwlock_unlock(&reg->rwlock);
    return true;
}

bool registry_write(registry_entry_t *reg, const char *new_val) {
    if (pthread_rwlock_wrlock(&reg->rwlock) != 0) {
        return false;
    }
    strncpy(reg->value, new_val, sizeof(reg->value) - 1);
    reg->value[sizeof(reg->value) - 1] = '\0';
    pthread_rwlock_unlock(&reg->rwlock);
    return true;
}

void registry_destroy(registry_entry_t *reg) {
    pthread_rwlock_destroy(&reg->rwlock);
}
