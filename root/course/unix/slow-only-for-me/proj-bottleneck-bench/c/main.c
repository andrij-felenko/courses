#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <pthread.h>
#include <stdint.h>
#include <time.h>
#include <errno.h>

#define THREAD_COUNT 8
#define LOCK_ITERATIONS 5000000
#define SYSCALL_ITERATIONS 2000000
#define IO_ITERATIONS 2000

/* Режим 1: Чисте обчислювальне навантаження (CPU-bound) */
void run_cpu_bound(void) {
    printf("[CPU-bound] Старт математичного циклу. Перевіряйте: perf top -p %d\n", getpid());
    volatile uint64_t hash = 0x123456789ABCDEF0ULL;
    while (1) {
        for (uint64_t i = 0; i < 100000000ULL; ++i) {
            hash ^= (i + 0x9e3779b9 + (hash << 6) + (hash >> 2));
        }
        /* Невелика пауза для перевірки сигналів переривання */
        usleep(1000);
    }
}

/* Режим 2: Шторм системних викликів (Kernel-bound) */
void run_syscall_bound(void) {
    printf("[Kernel-bound] Старт шторму викликів write(). Перевіряйте: strace -c -p %d\n", getpid());
    int fd = open("/dev/null", O_WRONLY);
    if (fd < 0) {
        perror("open /dev/null");
        return;
    }

    char byte = 'A';
    while (1) {
        for (size_t i = 0; i < SYSCALL_ITERATIONS; ++i) {
            if (write(fd, &byte, 1) != 1) {
                perror("write error");
                break;
            }
        }
        usleep(10000);
    }
    close(fd);
}

/* Режим 3: Конкуренція за блокування (Lock / Futex Contention) */
static pthread_mutex_t g_mutex = PTHREAD_MUTEX_INITIALIZER;
static volatile uint64_t g_shared_counter = 0;

void *lock_worker_thread(void *arg) {
    (void)arg;
    while (1) {
        for (size_t i = 0; i < 100000; ++i) {
            pthread_mutex_lock(&g_mutex);
            g_shared_counter++;
            pthread_mutex_unlock(&g_mutex);
        }
        usleep(1000);
    }
    return NULL;
}

void run_lock_contention(void) {
    printf("[Lock-bound] Старт 8 потоків із спільним м'ютексом. Перевіряйте: pidstat -w -p %d\n", getpid());
    pthread_t threads[THREAD_COUNT];
    for (int i = 0; i < THREAD_COUNT; ++i) {
        if (pthread_create(&threads[i], NULL, lock_worker_thread, NULL) != 0) {
            perror("pthread_create");
            return;
        }
    }
    for (int i = 0; i < THREAD_COUNT; ++i) {
        pthread_join(threads[i], NULL);
    }
}

/* Режим 4: Синхронний I/O (I/O-bound, стан D) */
void run_io_bound(void) {
    const char *test_file = "/tmp/bottleneck_sync.tmp";
    printf("[I/O-bound] Старт синхронного запису у %s. Перевіряйте: iostat -xz 1\n", test_file);
    
    int fd = open(test_file, O_WRONLY | O_CREAT | O_TRUNC | O_SYNC, 0644);
    if (fd < 0) {
        perror("open sync file");
        return;
    }

    char buffer[4096];
    memset(buffer, 'Z', sizeof(buffer));

    while (1) {
        for (size_t i = 0; i < IO_ITERATIONS; ++i) {
            if (write(fd, buffer, sizeof(buffer)) != (ssize_t)sizeof(buffer)) {
                perror("write sync");
                break;
            }
            fdatasync(fd);
        }
        lseek(fd, 0, SEEK_SET);
    }
    close(fd);
}

int main(int argc, char **argv) {
    if (argc < 2) {
        fprintf(stderr, "Використання: %s [cpu|syscall|lock|io]\n", argv[0]);
        return 1;
    }

    printf("PID процесу: %d\n", getpid());

    if (strcmp(argv[1], "cpu") == 0) {
        run_cpu_bound();
    } else if (strcmp(argv[1], "syscall") == 0) {
        run_syscall_bound();
    } else if (strcmp(argv[1], "lock") == 0) {
        run_lock_contention();
    } else if (strcmp(argv[1], "io") == 0) {
        run_io_bound();
    } else {
        fprintf(stderr, "Невідомий режим: %s\n", argv[1]);
        return 1;
    }
    return 0;
}
