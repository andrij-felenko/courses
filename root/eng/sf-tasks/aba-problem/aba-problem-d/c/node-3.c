#include <stdatomic.h>
#include <stdbool.h>
#include <stdlib.h>
#include <stdint.h>

typedef struct Node {
    int data;
    struct Node* next;
} Node;

typedef struct DeferredNode {
    Node* ptr;
    uint64_t epoch_retired;
} DeferredNode;

typedef struct ThreadState {
    _Atomic bool active;
    _Atomic uint64_t local_epoch;
} ThreadState;

typedef struct EpochManager {
    _Atomic uint64_t global_epoch;
} EpochManager;

void ebr_enter_critical(EpochManager* mgr, ThreadState* tstate) {
    atomic_store_explicit(&tstate->active, true, memory_order_relaxed);
    uint64_t current = atomic_load_explicit(&mgr->global_epoch, memory_order_acquire);
    atomic_store_explicit(&tstate->local_epoch, current, memory_order_relaxed);
}

void ebr_leave_critical(ThreadState* tstate) {
    atomic_store_explicit(&tstate->active, false, memory_order_release);
}

void ebr_retire_node(EpochManager* mgr, Node* node, DeferredNode* limbo, size_t* count) {
    uint64_t current = atomic_load_explicit(&mgr->global_epoch, memory_order_relaxed);
    limbo[*count].ptr = node;
    limbo[*count].epoch_retired = current;
    (*count)++;
}

void ebr_try_reclaim(EpochManager* mgr, ThreadState** threads, size_t num_threads, DeferredNode* limbo, size_t* count) {
    uint64_t current = atomic_load_explicit(&mgr->global_epoch, memory_order_relaxed);
    for (size_t i = 0; i < num_threads; ++i) {
        if (atomic_load_explicit(&threads[i]->active, memory_order_acquire)) {
            if (atomic_load_explicit(&threads[i]->local_epoch, memory_order_relaxed) != current) {
                return;
            }
        }
    }
    atomic_fetch_add_explicit(&mgr->global_epoch, 1, memory_order_acq_rel);
    size_t new_count = 0;
    for (size_t i = 0; i < *count; ++i) {
        if (current >= limbo[i].epoch_retired + 2) {
            free(limbo[i].ptr);
        } else {
            limbo[new_count++] = limbo[i];
        }
    }
    *count = new_count;
}
