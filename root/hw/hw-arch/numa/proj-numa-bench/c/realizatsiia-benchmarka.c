#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <time.h>
#include <sched.h>
#include <unistd.h>
#include <numa.h>
#include <numaif.h>

#define BUFFER_SIZE (256 * 1024 * 1024) // 256 МБ
#define LAT_NODES   (4 * 1024 * 1024)   // 4M елементів (256 МБ)
#define ITERATIONS  5

static uint64_t get_time_ns(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (uint64_t)ts.tv_sec * 1000000000ULL + (uint64_t)ts.tv_nsec;
}

// Прив'язка потоку до першого ядра вказаного вузла
static int bind_to_node_cpu(int node) {
    struct bitmask *cpus = numa_allocate_cpumask();
    if (numa_node_to_cpus(node, cpus) != 0) {
        numa_bitmask_free(cpus);
        return -1;
    }

    int target_cpu = -1;
    for (unsigned int i = 0; i < cpus->size; ++i) {
        if (numa_bitmask_isbitset(cpus, i)) {
            target_cpu = (int)i;
            break;
        }
    }
    numa_bitmask_free(cpus);

    if (target_cpu < 0) return -1;

    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);
    CPU_SET(target_cpu, &cpuset);
    return sched_setaffinity(0, sizeof(cpu_set_t), &cpuset);
}

// 1. Тест пропускної здатності (послідовне читання)
static double run_bandwidth_test(const uint64_t *buffer, size_t count) {
    uint64_t sink = 0;
    uint64_t start_ns = get_time_ns();

    for (int iter = 0; iter < ITERATIONS; ++iter) {
        for (size_t i = 0; i < count; i += 8) {
            sink += buffer[i];
        }
    }

    uint64_t duration_ns = get_time_ns() - start_ns;
    if (sink == 0xdeadbeef) printf("Sink\n");

    double total_bytes = (double)count * sizeof(uint64_t) * ITERATIONS;
    double duration_sec = (double)duration_ns / 1e9;
    return (total_bytes / duration_sec) / (1024.0 * 1024.0 * 1024.0); // ГБ/с
}

// 2. Тест чистої затримки (обхід випадкового списку покажчиків)
static double run_latency_test(const uint32_t *indices, size_t count, size_t steps) {
    uint32_t current = 0;
    uint64_t start_ns = get_time_ns();

    for (size_t s = 0; s < steps; ++s) {
        current = indices[current]; // непередбачуваний стрибок на нову кеш-лінію
    }

    uint64_t duration_ns = get_time_ns() - start_ns;
    if (current == 0xdeadbeef) printf("Sink\n");

    return (double)duration_ns / (double)steps; // наносекунд на одну операцію
}

int main(void) {
    if (numa_available() < 0) {
        fprintf(stderr, "Помилка: NUMA не підтримується на цій системі.\n");
        return EXIT_FAILURE;
    }

    int max_node = numa_max_node();
    printf("Кількість доступних NUMA-вузлів: %d\n", max_node + 1);
    if (max_node < 1) {
        printf("Для повноцінного тесту потрібно щонайменше 2 вузли.\n");
        return EXIT_SUCCESS;
    }

    // Виділяємо пам'ять суворо на Вузлі 0
    size_t count = BUFFER_SIZE / sizeof(uint64_t);
    uint64_t *bw_buf = (uint64_t *)numa_alloc_onnode(BUFFER_SIZE, 0);
    uint32_t *lat_buf = (uint32_t *)numa_alloc_onnode(LAT_NODES * sizeof(uint32_t), 0);

    if (!bw_buf || !lat_buf) {
        perror("numa_alloc_onnode failed");
        return EXIT_FAILURE;
    }

    // Ініціалізація буфера пропускної здатності
    for (size_t i = 0; i < count; ++i) {
        bw_buf[i] = i ^ 0x5555555555555555ULL;
    }

    // Створення псевдовипадкового циклу з кроком 64 байти (16 елементів uint32_t)
    size_t stride_elements = 16;
    size_t num_lines = LAT_NODES / stride_elements;
    size_t *perm = (size_t *)malloc(num_lines * sizeof(size_t));
    for (size_t i = 0; i < num_lines; ++i) perm[i] = i;

    // Перемішування Фішера-Єйтса
    srand(42);
    for (size_t i = num_lines - 1; i > 0; --i) {
        size_t j = (size_t)rand() % (i + 1);
        size_t tmp = perm[i];
        perm[i] = perm[j];
        perm[j] = tmp;
    }

    // Формуємо циклічний список у пам'яті
    for (size_t i = 0; i < num_lines; ++i) {
        size_t curr_idx = perm[i] * stride_elements;
        size_t next_idx = perm[(i + 1) % num_lines] * stride_elements;
        lat_buf[curr_idx] = (uint32_t)next_idx;
    }
    free(perm);

    // --- Тестування Вузла 0 (Локальний доступ) ---
    bind_to_node_cpu(0);
    printf("\n=== Тест 1: Локальний доступ (ЦП 0 -> RAM 0) ===\n");
    double loc_bw = run_bandwidth_test(bw_buf, count);
    printf("  Пропускна здатність : %.2f ГБ/с\n", loc_bw);
    double loc_lat = run_latency_test(lat_buf, LAT_NODES, 20000000);
    printf("  Затримка (Pointer Chase) : %.2f нс\n", loc_lat);

    // --- Тестування Вузла 1 (Віддалений доступ) ---
    bind_to_node_cpu(1);
    printf("\n=== Тест 2: Віддалений доступ (ЦП 1 -> RAM 0) ===\n");
    double rem_bw = run_bandwidth_test(bw_buf, count);
    printf("  Пропускна здатність : %.2f ГБ/с\n", rem_bw);
    double rem_lat = run_latency_test(lat_buf, LAT_NODES, 20000000);
    printf("  Затримка (Pointer Chase) : %.2f нс\n", rem_lat);

    // --- Підсумок ---
    printf("\n=== Підсумок NUMA Ratio ===\n");
    printf("  Відношення пропускної здатності : %.2f×\n", loc_bw / rem_bw);
    printf("  Відношення затримок доступу      : %.2f× (штраф +%.1f нс)\n",
           rem_lat / loc_lat, rem_lat - loc_lat);

    numa_free(bw_buf, BUFFER_SIZE);
    numa_free(lat_buf, LAT_NODES * sizeof(uint32_t));
    return EXIT_SUCCESS;
}
