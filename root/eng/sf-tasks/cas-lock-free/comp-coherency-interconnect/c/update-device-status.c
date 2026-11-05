#include <stdbool.h>
#include <stdint.h>
#include <stdatomic.h>

typedef struct {
    uint16_t status_flags;
    uint16_t sequence_number;
} device_state_t;

typedef union {
    device_state_t state;
    uint32_t raw;
} atomic_state_t;

static _Atomic uint32_t g_system_state = 0;

// Атомарне оновлення прапорців статусу з автоматичним інкрементом лічильника послідовності
bool update_device_status(uint16_t set_flags, uint16_t clear_flags) {
    uint32_t current_raw = atomic_load_explicit(&g_system_state, memory_order_relaxed);
    atomic_state_t old_val;
    atomic_state_t new_val;

    do {
        old_val.raw = current_raw;
        new_val.raw = current_raw;
        
        // Модифікація локальної копії стану
        new_val.state.status_flags = (old_val.state.status_flags & ~clear_flags) | set_flags;
        new_val.state.sequence_number = old_val.state.sequence_number + 1;

        // Слабкий CAS у циклі очікування: оптимально для ARM/RISC-V LL/SC
    } while (!atomic_compare_exchange_weak_explicit(
        &g_system_state,
        &current_raw,
        new_val.raw,
        memory_order_release,
        memory_order_relaxed));

    return true;
}
