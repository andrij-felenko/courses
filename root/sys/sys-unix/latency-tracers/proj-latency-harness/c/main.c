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
#include <math.h>

#define NSEC_PER_SEC 1000000000L
#define NSEC_PER_USEC 1000L

/* Захисна нормалізація структури timespec */
static inline void timespec_normalize(struct timespec *ts) {
    while (ts->tv_nsec >= NSEC_PER_SEC) {
        ts->tv_nsec -= NSEC_PER_SEC;
        ts->tv_sec += 1;
    }
}

/* Автоматичне тригерування зупинки ftrace через sysfs */
static void trigger_ftrace_stop(const char *reason, long latency_us) {
    int fd = open("/sys/kernel/tracing/tracing_on", O_WRONLY);
    if (fd >= 0) {
        write(fd, "0", 1);
        close(fd);
        printf("[CRITICAL] ftrace stopped! Reason: %s (latency: %ld us)\n", reason, latency_us);
    } else {
        perror("Failed to open tracing_on");
    }
}

int main(int argc, char *argv[]) {
    int cpu_id = 1;
    int priority = 95;
    long period_us = 1000; /* 1 мс */
    long threshold_us = 20; /* Поріг аномалії: 20 мкс */
    int iterations = 10000;

    if (argc > 1) cpu_id = atoi(argv[1]);
    if (argc > 2) threshold_us = atol(argv[2]);

    printf("=== Real-Time Latency Harness (C POSIX) ===\n");
    printf("Target CPU: %d, Priority: SCHED_FIFO %d, Period: %ld us, Threshold: %ld us\n",
           cpu_id, priority, period_us, threshold_us);

    /* 1. Блокування пам'яті для виключення Page Faults */
    if (mlockall(MCL_CURRENT | MCL_FUTURE) != 0) {
        perror("mlockall failed");
        return EXIT_FAILURE;
    }

    /* 2. Прив'язка до процесорного ядра (CPU Affinity) */
    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);
    CPU_SET(cpu_id, &cpuset);
    if (pthread_setaffinity_np(pthread_self(), sizeof(cpu_set_t), &cpuset) != 0) {
        perror("pthread_setaffinity_np failed");
        return EXIT_FAILURE;
    }

    /* 3. Встановлення політики та пріоритету реального часу */
    struct sched_param param;
    param.sched_priority = priority;
    if (sched_setscheduler(0, SCHED_FIFO, &param) != 0) {
        perror("sched_setscheduler failed");
        return EXIT_FAILURE;
    }

    /* 4. Ініціалізація змінних статистики */
    long min_lat = 999999L;
    long max_lat = -999999L;
    double sum_lat = 0.0;
    double sum_sq_lat = 0.0;

    struct timespec next_period;
    if (clock_gettime(CLOCK_MONOTONIC, &next_period) != 0) {
        perror("clock_gettime failed");
        return EXIT_FAILURE;
    }

    /* Виконуємо попередній розігрів стеку (stack warm-up) */
    unsigned char dummy_stack[8192];
    memset(dummy_stack, 0, sizeof(dummy_stack));

    for (int i = 0; i < iterations; i++) {
        /* Обчислюємо наступну абсолютну часову мітку */
        next_period.tv_nsec += period_us * NSEC_PER_USEC;
        timespec_normalize(&next_period);

        /* Абсолютний сон до наступного періоду */
        int ret = clock_nanosleep(CLOCK_MONOTONIC, TIMER_ABSTIME, &next_period, NULL);
        if (ret != 0 && ret != EINTR) {
            fprintf(stderr, "clock_nanosleep failed: %s\n", strerror(ret));
            break;
        }

        /* Зчитуємо фактичний час пробудження */
        struct timespec now;
        clock_gettime(CLOCK_MONOTONIC, &now);

        /* Обчислюємо затримку у мікросекундах */
        long diff_sec = now.tv_sec - next_period.tv_sec;
        long diff_nsec = now.tv_nsec - next_period.tv_nsec;
        long latency_us = (diff_sec * NSEC_PER_SEC + diff_nsec) / NSEC_PER_USEC;

        if (latency_us < min_lat) min_lat = latency_us;
        if (latency_us > max_lat) max_lat = latency_us;
        sum_lat += latency_us;
        sum_sq_lat += (double)latency_us * latency_us;

        /* Перевірка порогу аномалії */
        if (latency_us > threshold_us) {
            trigger_ftrace_stop("Latency threshold exceeded", latency_us);
            break;
        }
    }

    double avg_lat = sum_lat / iterations;
    double stddev_lat = sqrt((sum_sq_lat / iterations) - (avg_lat * avg_lat));

    printf("\n=== Результати вимірювання затримок ===\n");
    printf("Ітерацій: %d\n", iterations);
    printf("Мінімальна затримка:  %ld us\n", min_lat);
    printf("Середня затримка:     %.2f us\n", avg_lat);
    printf("Максимальна затримка: %ld us\n", max_lat);
    printf("Стандартне відхилення: %.2f us\n", stddev_lat);

    return EXIT_SUCCESS;
}
