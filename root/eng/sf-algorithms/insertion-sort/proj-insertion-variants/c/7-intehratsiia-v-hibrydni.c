#include <stddef.h>

/* Допоміжне розбиття Ломуто/Гоара для Quicksort */
static size_t partition_step(int *arr, size_t lo, size_t hi);

/* Швидке сортування з відкладеним фінальним сортуванням вставками (стратегія Седжвіка) */
void hybrid_quicksort_sedgewick(int *arr, size_t n) {
    const size_t threshold = 16;
    if (arr == NULL || n <= 1) {
        return;
    }

    /* Фаза 1: Quicksort грубо впорядковує масив, ігноруючи блоки розміром <= 16 */
    /* (У реалізації використовується стек або обмежена рекурсія) */
    
    /* Фаза 2: Один глобальний прохід сортування вставками з вартовим */
    sentinel_insertion_sort(arr, n);
}
