#include <stdatomic.h>
#include <stdint.h>
#include <stdbool.h>

/* Атомарні змінні C11 */
atomic_uint_fast32_t g_atomic_counter = 0;
atomic_bool g_atomic_flag = false;

void update_counter(void) {
    /* Атомарне додавання без вимкнення переривань (fetch_add) */
    atomic_fetch_add_explicit(&g_atomic_counter, 1, memory_order_relaxed);
    
    /* Атомарне виставлення прапорця з гарантією публікації даних */
    atomic_store_explicit(&g_atomic_flag, true, memory_order_release);
}

bool check_and_clear_flag(void) {
    /* Атомарний обмін (зчитує старе значення і записує false) */
    return atomic_exchange_explicit(&g_atomic_flag, false, memory_order_acquire);
}
