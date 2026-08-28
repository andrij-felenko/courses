#define _GNU_SOURCE
#include <sys/mman.h>
#include <sys/resource.h>
#include <sys/time.h>
#include <time.h>
#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define BENCH_TOTAL_BYTES (1024ULL * 1024ULL * 1024ULL) /* 1 Гігабайт */

struct BenchmarkResult {
    const char *name;
    double wall_time_sec;
    double user_cpu_sec;
    double sys_cpu_sec;
    long voluntary_ctxt_switches;
    long involuntary_ctxt_switches;
    double throughput_gbps;
};

void run_benchmark_suite(void) {
    /* Створюємо анонімний файл у пам'яті (tmpfs) для усунення дискових затримок */
    int fd_src = memfd_create("bench_source", 0);
    int fd_dst = memfd_create("bench_dest", 0);

    if (fd_src < 0 || fd_dst < 0) {
        perror("memfd_create");
        return;
    }

    ftruncate(fd_src, BENCH_TOTAL_BYTES);
    ftruncate(fd_dst, BENCH_TOTAL_BYTES);

    /* Заповнюємо джерело тестовими даними */
    void *src_map = mmap(NULL, BENCH_TOTAL_BYTES, PROT_READ | PROT_WRITE, MAP_SHARED, fd_src, 0);
    if (src_map != MAP_FAILED) {
        memset(src_map, 0xAB, BENCH_TOTAL_BYTES);
        munmap(src_map, BENCH_TOTAL_BYTES);
    }

    printf("=== БЕНЧМАРК ВВОДУ-ВИВОДУ: ПЕРЕДАЧА 1 ГБ ДАНИХ У RAM ===\n\n");

    close(fd_src);
    close(fd_dst);
}
