#include <stdio.h>
#include <stdint.h>

void execute_distributed_worker(uint32_t my_node_id) {
    dsm_config_t config = {
        .shared_heap_size = 1024 * 1024 * 16, /* 16 МБ */
        .node_id = my_node_id,
        .total_nodes = 2,
        .enable_simd_diff = true
    };

    if (dsm_init(&config) != DSM_SUCCESS) {
        fprintf(stderr, "Помилка ініціалізації середовища DSM\n");
        return;
    }

    /* Виділяємо спільний масив на 8192 байти (2 сторінки) */
    uint64_t *shared_data = (uint64_t*)dsm_alloc_shared(8192);
    if (!shared_data) {
        dsm_destroy();
        return;
    }

    /* Стартовий бар'єр синхронізації */
    dsm_barrier(0);

    /* Вузол 0 модифікує перше 64-бітне слово, Вузол 1 — десяте */
    if (my_node_id == 0) {
        dsm_lock_acquire(100);
        shared_data[0] = 0xDEADBEEFCAFEBABE;
        dsm_lock_release(100);
    } else if (my_node_id == 1) {
        dsm_lock_acquire(200);
        shared_data[10] = 0x0123456789ABCDEF;
        dsm_lock_release(200);
    }

    /* Фінальний бар'єр для злиття відмінностей */
    dsm_barrier(1);

    /* Обидва вузли гарантовано бачать коректні зміни сусіда */
    dsm_free_shared(shared_data);
    dsm_destroy();
}
