#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <unistd.h>
#include <pthread.h>
#include <time.h>
#include <errno.h>
#include <sys/mman.h>
#include <numa.h>
#include <numaif.h>

#define BUFFER_SIZE (128 * 1024 * 1024) /* 128 МіБ */
#define PAGE_SIZE_4K 4096
#define NUM_PAGES (BUFFER_SIZE / PAGE_SIZE_4K)
#define NUM_ITERATIONS 5

/* Структура для передачі параметрів у робочий потік */
typedef struct {
    int target_cpu;
    int target_node;
    uint8_t *buffer;
    size_t size;
    double elapsed_ms;
    double bandwidth_gbs;
} thread_task_t;

/* Функція точного вимірювання часу в мілісекундах */
static double get_time_ms(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (double)ts.tv_sec * 1000.0 + (double)ts.tv_nsec / 1000000.0;
}

/* Перевірка фактичного розташування сторінок у NUMA-вузлах через move_pages */
static void inspect_page_locations(void *addr, size_t num_pages) {
    void **pages = malloc(num_pages * sizeof(void *));
    int *status = malloc(num_pages * sizeof(int));
    if (!pages || !status) {
        perror("malloc failed");
        free(pages);
        free(status);
        return;
    }

    uint8_t *base = (uint8_t *)addr;
    for (size_t i = 0; i < num_pages; ++i) {
        pages[i] = base + i * PAGE_SIZE_4K;
        status[i] = -1;
    }

    /* Якщо nodes == NULL, move_pages лише зчитує поточний стан сторінок */
    if (move_pages(0, num_pages, pages, NULL, status, 0) != 0) {
        perror("move_pages query failed");
    } else {
        int counts[8] = {0};
        int other = 0;
        for (size_t i = 0; i < num_pages; ++i) {
            if (status[i] >= 0 && status[i] < 8) {
                counts[status[i]]++;
            } else {
                other++;
            }
        }
        printf("  [Розподіл фізичних сторінок]: ");
        for (int n = 0; n < numa_num_configured_nodes(); ++n) {
            printf("Вузол %d: %d ст. (%.1f%%) | ", n, counts[n],
                   (double)counts[n] * 100.0 / (double)num_pages);
        }
        if (other > 0) printf("Не виділено/інші: %d ст.", other);
        printf("\n");
    }

    free(pages);
    free(status);
}

/* Робочий потік: прив'язується до CPU та вимірює швидкість читання пам'яті */
static void *benchmark_worker(void *arg) {
    thread_task_t *task = (thread_task_t *)arg;

    /* Прив'язка потоку до конкретного процесорного ядра (affinity) */
    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);
    CPU_SET(task->target_cpu, &cpuset);
    if (pthread_setaffinity_np(pthread_self(), sizeof(cpu_set_t), &cpuset) != 0) {
        perror("pthread_setaffinity_np failed");
    }

    /* Підігрів кешу процесора */
    volatile uint64_t sum = 0;
    uint64_t *ptr = (uint64_t *)task->buffer;
    size_t count = task->size / sizeof(uint64_t);

    double t_start = get_time_ms();
    for (int it = 0; it < NUM_ITERATIONS; ++it) {
        sum = 0;
        for (size_t i = 0; i < count; i += 8) {
            sum += ptr[i] + ptr[i+1] + ptr[i+2] + ptr[i+3];
        }
    }
    double t_end = get_time_ms();

    task->elapsed_ms = (t_end - t_start) / NUM_ITERATIONS;
    double total_gigabytes = (double)task->size / (1024.0 * 1024.0 * 1024.0);
    task->bandwidth_gbs = total_gigabytes / (task->elapsed_ms / 1000.0);

    return NULL;
}

int main(void) {
    if (numa_available() < 0) {
        fprintf(stderr, "NUMA не підтримується цим ядром або обладнанням.\n");
        return 1;
    }

    int num_nodes = numa_num_configured_nodes();
    int num_cpus = numa_num_configured_cpus();
    printf("=== ДІАГНОСТИКА СИСТЕМИ NUMA ===\n");
    printf("Виявлено NUMA-вузлів: %d, логічних процесорів: %d\n", num_nodes, num_cpus);

    for (int n = 0; n < num_nodes; ++n) {
        long long free_bytes = 0;
        long long total_bytes = numa_node_size64(n, &free_bytes);
        printf("  Вузол %d: Пам'ять: %.2f ГіБ (Вільно: %.2f ГіБ) | Відстань до інших: ",
               n, (double)total_bytes / (1024*1024*1024), (double)free_bytes / (1024*1024*1024));
        for (int m = 0; m < num_nodes; ++m) {
            printf("%d->%d=%d ", n, m, numa_distance(n, m));
        }
        printf("\n");
    }

    if (num_nodes < 2) {
        printf("\nДля тестування локального проти віддаленого доступу потрібно мінімум 2 вузли.\n");
        return 0;
    }

    /* 1. Тест MPOL_BIND на Вузол 0 */
    printf("\n--- ТЕСТ 1: Пам'ять прив'язана до Вузла 0 (MPOL_BIND) ---\n");
    void *buf_node0 = numa_alloc_onnode(BUFFER_SIZE, 0);
    if (!buf_node0) {
        perror("numa_alloc_onnode failed");
        return 1;
    }
    /* Перший дотик (First-touch): ініціалізуємо пам'ять */
    memset(buf_node0, 0xAA, BUFFER_SIZE);
    inspect_page_locations(buf_node0, NUM_PAGES);

    /* Тестуємо доступ із процесора Вузла 0 (Локальний доступ) */
    struct bitmask *cpus_node0 = numa_allocate_cpumask();
    struct bitmask *cpus_node1 = numa_allocate_cpumask();
    numa_node_to_cpus(0, cpus_node0);
    numa_node_to_cpus(1, cpus_node1);

    int cpu_node0 = -1, cpu_node1 = -1;
    for (int i = 0; i < num_cpus; ++i) {
        if (cpu_node0 == -1 && numa_bitmask_isbitset(cpus_node0, i)) cpu_node0 = i;
        if (cpu_node1 == -1 && numa_bitmask_isbitset(cpus_node1, i)) cpu_node1 = i;
    }

    pthread_t th0, th1;
    thread_task_t task_local = {cpu_node0, 0, (uint8_t*)buf_node0, BUFFER_SIZE, 0, 0};
    thread_task_t task_remote = {cpu_node1, 1, (uint8_t*)buf_node0, BUFFER_SIZE, 0, 0};

    printf("Виконуємо тест на CPU %d (Вузол 0, Локальний доступ)...\n", cpu_node0);
    pthread_create(&th0, NULL, benchmark_worker, &task_local);
    pthread_join(th0, NULL);
    printf("  -> Локальний доступ: час = %.2f мс, пропускна здатність = %.2f ГБ/с\n",
           task_local.elapsed_ms, task_local.bandwidth_gbs);

    printf("Виконуємо тест на CPU %d (Вузол 1, Віддалений доступ до Вузла 0)...\n", cpu_node1);
    pthread_create(&th1, NULL, benchmark_worker, &task_remote);
    pthread_join(th1, NULL);
    printf("  -> Віддалений доступ: час = %.2f мс, пропускна здатність = %.2f ГБ/с\n",
           task_remote.elapsed_ms, task_remote.bandwidth_gbs);

    double penalty = (task_remote.elapsed_ms - task_local.elapsed_ms) / task_local.elapsed_ms * 100.0;
    printf("  [Штраф за віддалений доступ]: +%.1f%% часу виконання!\n", penalty);

    numa_free(buf_node0, BUFFER_SIZE);

    /* 2. Тест MPOL_INTERLEAVE */
    printf("\n--- ТЕСТ 2: Пам'ять із чергуванням сторінок (MPOL_INTERLEAVE) ---\n");
    void *buf_interleaved = numa_alloc_interleaved(BUFFER_SIZE);
    if (!buf_interleaved) {
        perror("numa_alloc_interleaved failed");
        return 1;
    }
    memset(buf_interleaved, 0xBB, BUFFER_SIZE);
    inspect_page_locations(buf_interleaved, NUM_PAGES);

    numa_free(buf_interleaved, BUFFER_SIZE);
    numa_free_cpumask(cpus_node0);
    numa_free_cpumask(cpus_node1);

    return 0;
}
