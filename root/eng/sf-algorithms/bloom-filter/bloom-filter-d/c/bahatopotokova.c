#include <numa.h>
#include <stdatomic.h>

/* Алокація бітового вектору на локальному NUMA-вузлі */
uint8_t *allocate_numa_bloom_bits(size_t bytes, int numa_node) {
    return (uint8_t *)numa_alloc_onnode(bytes, numa_node);
}

/* Безблокувальна атомарна вставка біта */
void bloom_set_bit_atomic(_Atomic uint8_t *bit_array, size_t bit_index) {
    _Atomic uint8_t *byte_ptr = &bit_array[bit_index >> 3];
    uint8_t mask = (uint8_t)(1u << (bit_index & 7));
    atomic_fetch_or_explicit(byte_ptr, mask, memory_order_relaxed);
}
