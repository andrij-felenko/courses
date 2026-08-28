#include <iostream>

void simulate_cache_eviction(size_t cache_ways, size_t access_count) {
    std::cout << "=== Кеш L1 (" << cache_ways << "-way associative) ===\n";
    if (access_count > cache_ways) {
        std::cout << "За принципом Діріхле " << access_count << " адрес > " 
                  << cache_ways << " слотів кешу.\n"
                  << "Витиснення ліній кешу математично НЕМОЖЛИВО уникнути!\n";
    }
}

int main() {
    simulate_cache_eviction(8, 9);
    return 0;
}
