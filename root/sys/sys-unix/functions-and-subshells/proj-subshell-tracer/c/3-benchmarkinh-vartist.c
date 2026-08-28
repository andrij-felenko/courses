#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/wait.h>
#include <sys/resource.h>
#include <time.h>

#define ITERATIONS 5000

static inline void in_process_function(volatile int *val) {
    *val += 1;
}

double measure_function_calls(void) {
    volatile int counter = 0;
    struct timespec start, end;
    clock_gettime(CLOCK_MONOTONIC, &start);

    for (int i = 0; i < ITERATIONS; i++) {
        in_process_function(&counter);
    }

    clock_gettime(CLOCK_MONOTONIC, &end);
    return (end.tv_sec - start.tv_sec) * 1e6 + (end.tv_nsec - start.tv_nsec) / 1e3;
}

double measure_subshell_forks(void) {
    struct timespec start, end;
    clock_gettime(CLOCK_MONOTONIC, &start);

    for (int i = 0; i < ITERATIONS; i++) {
        pid_t pid = fork();
        if (pid == 0) {
            _exit(0); // Імітуємо швидке завершення підоболонки
        }
        waitpid(pid, NULL, 0);
    }

    clock_gettime(CLOCK_MONOTONIC, &end);
    return (end.tv_sec - start.tv_sec) * 1e6 + (end.tv_nsec - start.tv_nsec) / 1e3;
}

int main(void) {
    printf("Benchmarking %d operations on current CPU...\n", ITERATIONS);
    double fn_time_us = measure_function_calls();
    double fork_time_us = measure_subshell_forks();

    printf("In-process Function Calls: %.2f us total (%.4f us per call)\n",
           fn_time_us, fn_time_us / ITERATIONS);
    printf("Subshell fork() Creation:  %.2f us total (%.2f us per fork)\n",
           fork_time_us, fork_time_us / ITERATIONS);
    printf("Cost Ratio: fork() is ~%.1f times slower than in-process function!\n",
           fork_time_us / fn_time_us);

    // Інспекція ресурсів ядра через getrusage
    struct rusage usage;
    if (getrusage(RUSAGE_CHILDREN, &usage) == 0) {
        printf("Kernel Telemetry for %d child subshells:\n", ITERATIONS);
        printf("  Minor Page Faults (COW events): %ld\n", usage.ru_minflt);
        printf("  Voluntary Context Switches:     %ld\n", usage.ru_nvcsw);
        printf("  Involuntary Context Switches:   %ld\n", usage.ru_nivcsw);
    }

    return 0;
}
