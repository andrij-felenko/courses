#include <stdio.h>

void simulate_cache_eviction(size_t cache_ways, size_t access_count) {
    printf("=== Кеш L1 (асоціативність: %zu шляхів) ===\n", cache_ways);
    printf("Спроба завантажити %zu блоків пам'яті в той самий кеш-набор:\n", access_count);

    if (access_count > cache_ways) {
        printf("РЕЗУЛЬТАТ: За принципом Діріхле, %zu блоків не вміщаються в %zu комірок.\n",
               access_count, cache_ways);
        printf("Виникає неминуче витиснення (Thrashing/Eviction) принаймні %zu блоків!\n",
               access_count - cache_ways);
    }
}

int main(void) {
    simulate_cache_eviction(8, 9);
    return 0;
}
