#include <stdatomic.h>
#include <stdbool.h>
#include <stdlib.h>

#define MAX_HAZARD_POINTERS 128
#define RETIRED_THRESHOLD 32

typedef struct {
    _Atomic(void*) pointer;
    _Atomic bool active;
} HazardPointerC;

HazardPointerC g_hp_array[MAX_HAZARD_POINTERS];

int acquire_hp_slot(void) {
    for (int i = 0; i < MAX_HAZARD_POINTERS; ++i) {
        bool expected = false;
        if (atomic_compare_exchange_strong(&g_hp_array[i].active, &expected, true)) {
            return i;
        }
    }
    return -1;
}

void release_hp_slot(int slot_idx) {
    if (slot_idx >= 0 && slot_idx < MAX_HAZARD_POINTERS) {
        atomic_store_explicit(&g_hp_array[slot_idx].pointer, NULL, memory_order_release);
        atomic_store_explicit(&g_hp_array[slot_idx].active, false, memory_order_release);
    }
}

void* protect_pointer(_Atomic(void*)* atomic_src, int slot_idx) {
    void* ptr = NULL;
    do {
        ptr = atomic_load_explicit(atomic_src, memory_order_relaxed);
        atomic_store_explicit(&g_hp_array[slot_idx].pointer, ptr, memory_order_seq_cst);
    } while (atomic_load_explicit(atomic_src, memory_order_acquire) != ptr);
    return ptr;
}
