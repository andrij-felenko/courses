#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <time.h>
#include <sched.h>
#include <pthread.h>
#include <sys/mman.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>
#include <limits.h>

#define ITERATIONS 10000
#define NSEC_PER_SEC 1000000000L
#define PERIOD_NSEC 1000000L /* 1 мілісекунда = 1 000 000 нс */
#define STACK_PREFAULT_SIZE (64 * 1024) /* 64 КБ — із запасом менше за межу стека */
#define PAGE_SIZE_BYTES 4096

/* Вимкнення C-states через /dev/cpu_dma_latency */
static int disable_cpu_cstates(void) {
    int fd = open("/dev/cpu_dma_latency", O_WRONLY);
    if (fd < 0) {
        perror("Не вдалося відкрити /dev/cpu_dma_latency");
        return -1;
    }
    int32_t latency = 0; // 0 мкс дозволеної затримки
    if (write(fd, &latency, sizeof(latency)) != sizeof(latency)) {
        perror("Не вдалося записати у /dev/cpu_dma_latency");
        close(fd);
        return -1;
    }
    return fd; // Утримуємо відкритим на весь час роботи
}

static void stack_prefault(void) {
    volatile unsigned char dummy[STACK_PREFAULT_SIZE];
    /* По байту в кожну сторінку: змушує ядро підставити фізичні сторінки стека */
    for (size_t i = 0; i < STACK_PREFAULT_SIZE; i += PAGE_SIZE_BYTES) {
        dummy[i] = 0;
    }
}

static inline void timespec_add_ns(struct timespec *ts, long ns) {
    ts->tv_nsec += ns;
    while (ts->tv_nsec >= NSEC_PER_SEC) {
        ts->tv_nsec -= NSEC_PER_SEC;
        ts->tv_sec += 1;
    }
}

int main(int argc, char *argv[]) {
    struct sched_param param;
    struct timespec t_next, t_actual;
    cpu_set_t cpuset;
    long min_lat = LONG_MAX, max_lat = LONG_MIN, total_lat = 0;
    int done = 0; /* скільки ітерацій справді виміряно */
    int target_cpu = 1;

    if (argc > 1) {
        target_cpu = atoi(argv[1]);
    }

    printf("Запуск тестування затримки реального часу на CPU %d...\n", target_cpu);

    /* 1. Блокування пам'яті */
    if (mlockall(MCL_CURRENT | MCL_FUTURE) != 0) {
        perror("mlockall failed (потрібні права CAP_IPC_LOCK)");
        return EXIT_FAILURE;
    }

    /* 2. Прогрів стека */
    stack_prefault();

    /* 3. Вимкнення енергозбереження C-states */
    int cstate_fd = disable_cpu_cstates();

    /* 4. Прив'язка до конкретного ядра CPU */
    CPU_ZERO(&cpuset);
    CPU_SET(target_cpu, &cpuset);
    /* pthread_* повертають код помилки й НЕ чіпають errno — perror тут збрехав би */
    int aff_ret = pthread_setaffinity_np(pthread_self(), sizeof(cpu_set_t), &cpuset);
    if (aff_ret != 0) {
        fprintf(stderr, "pthread_setaffinity_np failed: %s\n", strerror(aff_ret));
        munlockall();
        if (cstate_fd >= 0) close(cstate_fd);
        return EXIT_FAILURE;
    }

    /* 5. Встановлення RT-пріоритету SCHED_FIFO */
    memset(&param, 0, sizeof(param));
    param.sched_priority = 80;
    if (sched_setscheduler(0, SCHED_FIFO, &param) != 0) {
        perror("sched_setscheduler failed (потрібні права CAP_SYS_NICE)");
        munlockall();
        if (cstate_fd >= 0) close(cstate_fd);
        return EXIT_FAILURE;
    }

    /* 6. Початкова позначка часу */
    clock_gettime(CLOCK_MONOTONIC, &t_next);

    /* 7. Основний вимірювальний цикл */
    for (int i = 0; i < ITERATIONS; i++) {
        timespec_add_ns(&t_next, PERIOD_NSEC);

        int ret = clock_nanosleep(CLOCK_MONOTONIC, TIMER_ABSTIME, &t_next, NULL);
        if (ret != 0) {
            fprintf(stderr, "clock_nanosleep перервано: %s\n", strerror(ret));
            break;
        }

        clock_gettime(CLOCK_MONOTONIC, &t_actual);

        long diff_nsec = (t_actual.tv_sec - t_next.tv_sec) * NSEC_PER_SEC +
                         (t_actual.tv_nsec - t_next.tv_nsec);
        long diff_usec = diff_nsec / 1000;

        if (diff_usec < min_lat) min_lat = diff_usec;
        if (diff_usec > max_lat) max_lat = diff_usec;
        total_lat += diff_usec;
        done++;
    }

    /* Цикл могло обірвати сигналом на першій же ітерації — тоді міряти нічого */
    if (done == 0) {
        fprintf(stderr, "Жодної ітерації не виміряно.\n");
        if (cstate_fd >= 0) close(cstate_fd);
        munlockall();
        return EXIT_FAILURE;
    }

    printf("Результати тестування затримки (%d ітерацій):\n", done);
    printf("  Мінімальна затримка: %ld мкс\n", min_lat);
    printf("  Максимальна затримка: %ld мкс\n", max_lat);
    printf("  Середня затримка:    %.2f мкс\n", (double)total_lat / done);

    if (cstate_fd >= 0) close(cstate_fd);
    munlockall();
    return EXIT_SUCCESS;
}
