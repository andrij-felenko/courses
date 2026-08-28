/* cxl_allocator_bench.c */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <unistd.h>
#include <numa.h>
#include <numaif.h>
#include <sys/mman.h>
#include <x86intrin.h>

#define BUFFER_SIZE (1024ULL * 1024ULL * 1024ULL) // 1 ГБ
#define STRIDE 64 // 64 байти (розмір кеш-лінії)

// Функція пошуку першого CPU-less NUMA вузла (CXL Node)
static int find_cxl_numa_node(void) {
    if (numa_available() < 0) {
        fprintf(stderr, "Помилка: підсистема NUMA недоступна у ядрі\n");
        return -1;
    }

    int max_node = numa_max_node();
    struct bitmask *cpus = numa_allocate_cpumask();

    for (int n = 0; n <= max_node; n++) {
        long long free_mem = 0;  // numa_node_size64() чекає саме long long *
        long long node_size = numa_node_size64(n, &free_mem);
        
        if (node_size > 0) {
            numa_node_to_cpus(n, cpus);
            // Якщо на вузлі немає CPU ядер, але є пам'ять -> це CXL/Tier2
            if (numa_bitmask_weight(cpus) == 0) {
                numa_free_cpumask(cpus);
                return n;
            }
        }
    }

    numa_free_cpumask(cpus);
    return -1;
}

// Бенчмарк затримки випадкового читання пам'яті (Pointer Chasing)
static double measure_latency_ns(uint64_t *ptr, size_t count) {
    // Ініціалізація циклічного ланцюга переходів у ВИПАДКОВОМУ порядку.
    // Постійний крок (i + k) % count апаратний prefetcher розпізнає й
    // випереджає — саме цього бенчмарк і має уникнути. Тому перемішуємо
    // алгоритмом Саттоло: він дає рівно один цикл довжини count.
    for (size_t i = 0; i < count; i++) {
        ptr[i] = i;
    }
    uint64_t rnd = 88172645463325252ULL;   // xorshift64, фіксоване зерно
    for (size_t i = count - 1; i > 0; i--) {
        rnd ^= rnd << 13; rnd ^= rnd >> 7; rnd ^= rnd << 17;
        size_t j = (size_t)(rnd % i);      // строго j < i — умова Саттоло
        uint64_t tmp = ptr[i]; ptr[i] = ptr[j]; ptr[j] = tmp;
    }

    uint64_t idx = 0;
    uint64_t start_cycles = __rdtsc();
    
    // Виконання 10 мільйонів переходів
    const uint64_t iterations = 10000000ULL;
    for (uint64_t i = 0; i < iterations; i++) {
        idx = ptr[idx];
    }
    
    uint64_t end_cycles = __rdtsc();
    
    // Запобігаємо оптимізації компілятора
    if (idx == 0xFFFFFFFF) printf("checksum: %lu\n", (unsigned long)idx);

    double total_cycles = (double)(end_cycles - start_cycles);
    // rdtsc рахує такти НЕЗМІННОГО TSC — це номінальна частота процесора,
    // а не поточна. Тут підставлено 3.0 ГГц (1 такт = 0.333 нс); на іншому
    // залізі коефіцієнт треба взяти з реальної номінальної частоти.
    return (total_cycles / iterations) / 3.0; 
}

int main(void) {
    int cxl_node = find_cxl_numa_node();
    if (cxl_node < 0) {
        printf("CXL вузол не знайдено. Використовуємо вузол 0 як запасний.\n");
        cxl_node = 0;
    } else {
        printf("Знайдено пам'ять CXL на NUMA Node %d\n", cxl_node);
    }

    // Виділяємо пам'ять через mmap
    void *addr = mmap(NULL, BUFFER_SIZE, PROT_READ | PROT_WRITE,
                      MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    if (addr == MAP_FAILED) {
        perror("mmap failed");
        return 1;
    }

    // Прив'язуємо адресний простір до CXL вузла через mbind
    unsigned long nodemask = (1UL << cxl_node);
    if (mbind(addr, BUFFER_SIZE, MPOL_BIND, &nodemask, sizeof(nodemask) * 8, MPOL_MF_MOVE) < 0) {
        perror("mbind failed");
        munmap(addr, BUFFER_SIZE);
        return 1;
    }

    // Примусова ініціалізація сторінок (Fault-in)
    memset(addr, 1, BUFFER_SIZE);

    size_t element_count = BUFFER_SIZE / sizeof(uint64_t);
    double latency = measure_latency_ns((uint64_t *)addr, element_count);
    printf("Середня затримка доступу до пам'яті CXL: %.2f нс\n", latency);

    munmap(addr, BUFFER_SIZE);
    return 0;
}
