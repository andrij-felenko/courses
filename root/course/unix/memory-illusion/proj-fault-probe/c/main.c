#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <unistd.h>
#include <time.h>
#include <sys/mman.h>
#include <sys/resource.h>
#include <sys/wait.h>
#include <sys/types.h>

/* Структура для збереження зрізу метрик пам'яті */
typedef struct {
    long minflt;
    long majflt;
    size_t resident_pages;
    size_t total_pages;
    size_t smaps_rss_kb;
    size_t smaps_pss_kb;
    size_t smaps_private_dirty_kb;
    uint64_t elapsed_ns;
} memory_snapshot_t;

/* Отримання поточного монотонного часу в наносекундах */
static uint64_t get_time_ns(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTON, &ts);
    return (uint64_t)ts.tv_sec * 1000000000ULL + (uint64_t)ts.tv_nsec;
}

/* Читання підсумкових метрик з /proc/self/smaps_rollup */
static void read_smaps_metrics(size_t *rss_kb, size_t *pss_kb, size_t *private_dirty_kb) {
    *rss_kb = 0;
    *pss_kb = 0;
    *private_dirty_kb = 0;

    FILE *f = fopen("/proc/self/smaps_rollup", "r");
    if (!f) return;

    char line[256];
    while (fgets(line, sizeof(line), f)) {
        if (strncmp(line, "Rss:", 4) == 0) {
            sscanf(line + 4, "%zu", rss_kb);
        } else if (strncmp(line, "Pss:", 4) == 0) {
            sscanf(line + 4, "%zu", pss_kb);
        } else if (strncmp(line, "Private_Dirty:", 14) == 0) {
            sscanf(line + 14, "%zu", private_dirty_kb);
        }
    }
    fclose(f);
}

/* Отримання поточних лічильників збоїв та резидентності */
static memory_snapshot_t get_snapshot(void *addr, size_t length, size_t page_size) {
    memory_snapshot_t snap;
    memset(&snap, 0, sizeof(snap));
    snap.elapsed_ns = get_time_ns();

    struct rusage usage;
    if (getrusage(RUSAGE_SELF, &usage) == 0) {
        snap.minflt = usage.ru_minflt;
        snap.majflt = usage.ru_majflt;
    }

    read_smaps_metrics(&snap.smaps_rss_kb, &snap.smaps_pss_kb, &snap.smaps_private_dirty_kb);

    if (addr != NULL && length > 0) {
        snap.total_pages = length / page_size;
        unsigned char *vec = calloc(snap.total_pages, 1);
        if (vec) {
            if (mincore(addr, length, vec) == 0) {
                for (size_t i = 0; i < snap.total_pages; ++i) {
                    if (vec[i] & 1) {
                        snap.resident_pages++;
                    }
                }
            }
            free(vec);
        }
    }

    return snap;
}

/* Друк різниці між двома зрізами */
static void print_delta(const char *stage_name, memory_snapshot_t before, memory_snapshot_t after) {
    long d_minflt = after.minflt - before.minflt;
    long d_majflt = after.majflt - before.majflt;
    long d_res = (long)after.resident_pages - (long)before.resident_pages;
    uint64_t dur_us = (after.elapsed_ns - before.elapsed_ns) / 1000ULL;

    printf("[%-28s] Час: %4lu мкс | Збої: +%-3ld min, +%ld maj | DRAM: %3zu/%3zu стор. (+%ld) | RSS: %zu КіБ, PSS: %zu КіБ, PrivDirty: %zu КіБ\n",
           stage_name, dur_us, d_minflt, d_majflt, after.resident_pages, after.total_pages, d_res,
           after.smaps_rss_kb, after.smaps_pss_kb, after.smaps_private_dirty_kb);
}

/* Демонстрація 1: Demand Paging (Видача за вимогою) */
static void demo_demand_paging(size_t page_size) {
    printf("\n=== ТЕСТ 1: Demand Paging (Виділення 100 сторінок = %zu КіБ) ===\n",
           (100 * page_size) / 1024);
    const size_t num_pages = 100;
    const size_t total_bytes = num_pages * page_size;

    memory_snapshot_t s0 = get_snapshot(NULL, 0, page_size);

    /* 1. Виділяємо анонімну приватну пам'ять */
    volatile char *buffer = mmap(NULL, total_bytes, PROT_READ | PROT_WRITE,
                                 MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    if (buffer == MAP_FAILED) {
        perror("mmap");
        return;
    }

    /* Вимикаємо Transparent Huge Pages для точності експерименту */
    madvise((void *)buffer, total_bytes, MADV_NOHUGEPAGE);

    memory_snapshot_t s1 = get_snapshot((void *)buffer, total_bytes, page_size);
    print_delta("1. mmap() (чиста обіцянка)", s0, s1);

    /* 2. Читаємо перші 15 сторінок (Zero Page Optimization в Linux) */
    volatile char sink = 0;
    for (size_t i = 0; i < 15; ++i) {
        sink += buffer[i * page_size];
    }
    (void)sink;

    memory_snapshot_t s2 = get_snapshot((void *)buffer, total_bytes, page_size);
    print_delta("2. Читання 15 сторінок", s1, s2);

    /* 3. Записуємо у перші 40 сторінок */
    for (size_t i = 0; i < 40; ++i) {
        buffer[i * page_size] = (char)(i + 1);
    }

    memory_snapshot_t s3 = get_snapshot((void *)buffer, total_bytes, page_size);
    print_delta("3. Запис у 40 сторінок", s2, s3);

    /* 4. Повторний запис у ті самі 40 сторінок (сторінки вже в DRAM) */
    for (size_t i = 0; i < 40; ++i) {
        buffer[i * page_size] = (char)(i + 2);
    }

    memory_snapshot_t s4 = get_snapshot((void *)buffer, total_bytes, page_size);
    print_delta("4. Повторний запис у 40 стор.", s3, s4);

    /* 5. Запис у решту 60 сторінок */
    for (size_t i = 40; i < num_pages; ++i) {
        buffer[i * page_size] = (char)(i + 1);
    }

    memory_snapshot_t s5 = get_snapshot((void *)buffer, total_bytes, page_size);
    print_delta("5. Запис у решту 60 стор.", s4, s5);

    munmap((void *)buffer, total_bytes);
}

/* Демонстрація 2: Copy-on-Write (Поведінка при fork) */
static void demo_copy_on_write(size_t page_size) {
    printf("\n=== ТЕСТ 2: Copy-on-Write (Розгалуження через fork, 50 сторінок) ===\n");
    const size_t num_pages = 50;
    const size_t total_bytes = num_pages * page_size;

    volatile char *buffer = mmap(NULL, total_bytes, PROT_READ | PROT_WRITE,
                                 MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    if (buffer == MAP_FAILED) {
        perror("mmap");
        return;
    }
    madvise((void *)buffer, total_bytes, MADV_NOHUGEPAGE);

    /* Заповнюємо всі 50 сторінок даними перед викликом fork() */
    for (size_t i = 0; i < num_pages; ++i) {
        buffer[i * page_size] = (char)0xAA;
    }

    memory_snapshot_t s_parent_init = get_snapshot((void *)buffer, total_bytes, page_size);
    printf("Стан пам'яті батька до fork(): %zu/%zu резидентних сторінок\n",
           s_parent_init.resident_pages, s_parent_init.total_pages);

    pid_t pid = fork();
    if (pid < 0) {
        perror("fork");
        munmap((void *)buffer, total_bytes);
        return;
    }

    if (pid == 0) {
        /* Процес-дитина */
        memory_snapshot_t s_child_start = get_snapshot((void *)buffer, total_bytes, page_size);

        /* Дитина читає всі 50 сторінок — збоїв виникати не повинно */
        volatile char sum = 0;
        for (size_t i = 0; i < num_pages; ++i) {
            sum += buffer[i * page_size];
        }
        (void)sum;

        memory_snapshot_t s_child_read = get_snapshot((void *)buffer, total_bytes, page_size);
        print_delta("Дитина: читання 50 стор.", s_child_start, s_child_read);

        /* Дитина модифікує 20 сторінок — спрацьовує COW */
        for (size_t i = 0; i < 20; ++i) {
            buffer[i * page_size] = (char)0xBB;
        }

        memory_snapshot_t s_child_write = get_snapshot((void *)buffer, total_bytes, page_size);
        print_delta("Дитина: запис у 20 стор. (COW)", s_child_read, s_child_write);

        munmap((void *)buffer, total_bytes);
        _exit(0);
    } else {
        /* Процес-батько чекає на завершення дитини */
        int status;
        waitpid(pid, &status, 0);

        memory_snapshot_t s_parent_after_child = get_snapshot((void *)buffer, total_bytes, page_size);
        printf("\nПроцес-дитина завершився. Батько лишився єдиним власником.\n");

        /* Батько модифікує 20 сторінок, які дитина дублювала собі */
        for (size_t i = 0; i < 20; ++i) {
            buffer[i * page_size] = (char)0xCC;
        }

        memory_snapshot_t s_parent_write_split = get_snapshot((void *)buffer, total_bytes, page_size);
        print_delta("Батько: запис у 20 відколотих", s_parent_after_child, s_parent_write_split);

        /* Батько модифікує решту 30 сторінок, де він єдиний власник */
        for (size_t i = 20; i < num_pages; ++i) {
            buffer[i * page_size] = (char)0xDD;
        }

        memory_snapshot_t s_parent_write_sole = get_snapshot((void *)buffer, total_bytes, page_size);
        print_delta("Батько: запис у 30 спільних", s_parent_write_split, s_parent_write_sole);

        munmap((void *)buffer, total_bytes);
    }
}

int main(void) {
    long sc_res = sysconf(_SC_PAGESIZE);
    if (sc_res <= 0) {
        fprintf(stderr, "Не вдалося визначити розмір сторінки системи\n");
        return EXIT_FAILURE;
    }
    size_t page_size = (size_t)sc_res;
    printf("Розмір апаратної сторінки системи: %zu байтів\n", page_size);

    demo_demand_paging(page_size);
    demo_copy_on_write(page_size);

    return EXIT_SUCCESS;
}
