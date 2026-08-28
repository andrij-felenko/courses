#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <inttypes.h>
#include <string.h>
#include <pthread.h>
#include <sched.h>
#include <sys/mman.h>
#include <time.h>
#include <errno.h>

#define TARGET_CPU 1
#define ITERATIONS 10000000
#define JITTER_THRESHOLD_NS 1000

static inline uint64_t get_time_ns(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC_RAW, &ts);
    return (uint64_t)ts.tv_sec * 1000000000ULL + (uint64_t)ts.tv_nsec;
}

int setup_thread_isolation(int cpu_id) {
    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);
    CPU_SET(cpu_id, &cpuset);

    pthread_t thread = pthread_self();
    if (pthread_setaffinity_np(thread, sizeof(cpu_set_t), &cpuset) != 0) {
        perror("pthread_setaffinity_np failed");
        return -1;
    }

    struct sched_param param;
    param.sched_priority = 99; // Найвищий пріоритет SCHED_FIFO
    if (pthread_setschedparam(thread, SCHED_FIFO, &param) != 0) {
        perror("pthread_setschedparam failed (потрібні права root)");
        return -1;
    }

    if (mlockall(MCL_CURRENT | MCL_FUTURE) != 0) {
        perror("mlockall failed");
        return -1;
    }

    return 0;
}

int main(void) {
    printf("Ініціалізація ізоляції для CPU %d...\n", TARGET_CPU);
    if (setup_thread_isolation(TARGET_CPU) != 0) {
        fprintf(stderr, "Помилка налаштування ізоляції\n");
        return EXIT_FAILURE;
    }

    // Попереднє прогрівання пам'яті (запобігання page faults)
    volatile uint8_t dummy_buffer[1024 * 1024];
    memset((void*)dummy_buffer, 0, sizeof(dummy_buffer));

    printf("Запуск гарячого циклу вимірювання затримок...\n");

    uint64_t max_jitter_ns = 0;
    uint64_t prev_time = get_time_ns();

    for (uint64_t i = 0; i < ITERATIONS; ++i) {
        uint64_t current_time = get_time_ns();
        uint64_t delta = current_time - prev_time;
        prev_time = current_time;

        // Порожня ітерація коштує десятки наносекунд, тож усе, що довше
        // за поріг, — це втручання ззовні циклу, а сама дельта і є його ціна.
        if (i > 0 && delta > JITTER_THRESHOLD_NS) {
            if (delta > max_jitter_ns) {
                max_jitter_ns = delta;
            }
        }
    }

    printf("Вимірювання завершено.\n");
    printf("Максимальний OS jitter: %" PRIu64 " наносекунд\n", max_jitter_ns);

    return EXIT_SUCCESS;
}
