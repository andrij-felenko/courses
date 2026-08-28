#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <pthread.h>

typedef struct {
    uint64_t active_epoch;
    uint32_t active_major_version;
    pthread_rwlock_t rwlock;
} epoch_fencing_state_t;

typedef enum {
    EPOCH_STATUS_OK = 0,
    EPOCH_STATUS_STALE_GENERATION = 1,
    EPOCH_STATUS_MAJOR_MISMATCH = 2
} epoch_status_t;

bool epoch_coordinator_init(epoch_fencing_state_t *coordinator, uint64_t start_epoch, uint32_t major) {
    if (!coordinator) return false;
    coordinator->active_epoch = start_epoch;
    coordinator->active_major_version = major;
    return (pthread_rwlock_init(&coordinator->rwlock, NULL) == 0);
}

void epoch_coordinator_destroy(epoch_fencing_state_t *coordinator) {
    if (coordinator) {
        pthread_rwlock_destroy(&coordinator->rwlock);
    }
}

/* Перевірка токена перед виконанням мутації стану у змішаному парку */
epoch_status_t epoch_validate_mutation(epoch_fencing_state_t *coordinator,
                                       uint64_t request_epoch,
                                       uint32_t caller_major) {
    if (!coordinator) return EPOCH_STATUS_STALE_GENERATION;

    pthread_rwlock_rdlock(&coordinator->rwlock);

    if (request_epoch < coordinator->active_epoch) {
        pthread_rwlock_unlock(&coordinator->rwlock);
        return EPOCH_STATUS_STALE_GENERATION;
    }

    if (caller_major != coordinator->active_major_version) {
        pthread_rwlock_unlock(&coordinator->rwlock);
        return EPOCH_STATUS_MAJOR_MISMATCH;
    }

    pthread_rwlock_unlock(&coordinator->rwlock);
    return EPOCH_STATUS_OK;
}

/* Аварійне підвищення епохи при зупинці кампанії (Kill Switch) */
uint64_t epoch_advance_on_abort(epoch_fencing_state_t *coordinator) {
    if (!coordinator) return 0;
    pthread_rwlock_wrlock(&coordinator->rwlock);
    coordinator->active_epoch++;
    uint64_t new_epoch = coordinator->active_epoch;
    pthread_rwlock_unlock(&coordinator->rwlock);
    return new_epoch;
}
