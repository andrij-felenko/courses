#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <time.h>
#include <unistd.h>
#include <pthread.h>
#include <sys/wait.h>
#include <sys/types.h>

#define ITERATIONS 5000
#define NUM_WORKERS 100

// Допоміжна функція: отримання поточного часу в наносекундах
static inline uint64_t get_time_ns(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (uint64_t)ts.tv_sec * 1000000000ULL + (uint64_t)ts.tv_nsec;
}

// Допоміжна функція: зчитування Resident Set Size (VmRSS) у кілобайтах
static long get_rss_kb(void) {
    FILE *f = fopen("/proc/self/status", "r");
    if (!f) return -1;
    char line[256];
    long rss = -1;
    while (fgets(line, sizeof(line), f)) {
        if (strncmp(line, "VmRSS:", 6) == 0) {
            sscanf(line + 6, "%ld", &rss);
            break;
        }
    }
    fclose(f);
    return rss;
}

// Порожня функція для вимірювання створення потоку
static void *dummy_thread_fn(void *arg) {
    (void)arg;
    return NULL;
}

// ── ТЕСТ 1: Швидкість створення та очікування ─────────────────────────────
static void test_creation_latency(void) {
    printf("=== ТЕСТ 1: Швидкість створення та завершення (%d ітерацій) ===\n", ITERATIONS);

    // Вимірювання процесів (fork + waitpid)
    uint64_t start = get_time_ns();
    for (int i = 0; i < ITERATIONS; ++i) {
        pid_t pid = fork();
        if (pid == 0) {
            _exit(0);
        } else if (pid > 0) {
            int status = 0;
            waitpid(pid, &status, 0);
        }
    }
    uint64_t proc_duration = get_time_ns() - start;
    double proc_avg_us = (double)proc_duration / (ITERATIONS * 1000.0);

    // Вимірювання потоків (pthread_create + pthread_join)
    start = get_time_ns();
    for (int i = 0; i < ITERATIONS; ++i) {
        pthread_t tid;
        pthread_create(&tid, NULL, dummy_thread_fn, NULL);
        pthread_join(tid, NULL);
    }
    uint64_t thread_duration = get_time_ns() - start;
    double thread_avg_us = (double)thread_duration / (ITERATIONS * 1000.0);

    printf("  Процеси (fork + wait):  сер. час = %6.2f мкс на створення\n", proc_avg_us);
    printf("  Потоки (create + join): сер. час = %6.2f мкс на створення\n", thread_avg_us);
    printf("  -> Потоки створюються у %.1fx швидше за процеси\n\n", proc_avg_us / thread_avg_us);
}

// ── ТЕСТ 2: Затримка передачі 8 байтів даних ──────────────────────────────
static void test_ipc_vs_shared_mem(void) {
    printf("=== ТЕСТ 2: Затримка передачі даних (10 000 обмінів) ===\n");
    const int PING_PONG_COUNT = 10000;

    // 1. Міжпроцесний обмін через пайпи (IPC Pipe)
    int parent_to_child[2];
    int child_to_parent[2];
    if (pipe(parent_to_child) < 0 || pipe(child_to_parent) < 0) {
        perror("pipe");
        return;
    }

    uint64_t start = get_time_ns();
    pid_t pid = fork();
    if (pid == 0) {
        close(parent_to_child[1]);
        close(child_to_parent[0]);
        uint64_t val = 0;
        for (int i = 0; i < PING_PONG_COUNT; ++i) {
            if (read(parent_to_child[0], &val, sizeof(val)) <= 0) break;
            val++;
            if (write(child_to_parent[1], &val, sizeof(val)) <= 0) break;
        }
        close(parent_to_child[0]);
        close(child_to_parent[1]);
        _exit(0);
    } else {
        close(parent_to_child[0]);
        close(child_to_parent[1]);
        uint64_t val = 0;
        for (int i = 0; i < PING_PONG_COUNT; ++i) {
            if (write(parent_to_child[1], &val, sizeof(val)) <= 0) break;
            if (read(child_to_parent[0], &val, sizeof(val)) <= 0) break;
        }
        int status;
        waitpid(pid, &status, 0);
        close(parent_to_child[1]);
        close(child_to_parent[0]);
    }
    uint64_t pipe_time = get_time_ns() - start;
    double pipe_latency_us = (double)pipe_time / (PING_PONG_COUNT * 2 * 1000.0);

    // 2. Багатопотоковий обмін через спільну пам'ять із м'ютексом
    pthread_mutex_t mtx = PTHREAD_MUTEX_INITIALIZER;
    pthread_cond_t cv = PTHREAD_COND_INITIALIZER;
    volatile uint64_t shared_val = 0;
    volatile int turn = 0; // 0 - черга головного, 1 - черга воркера

    struct ThreadArg {
        pthread_mutex_t *mtx;
        pthread_cond_t *cv;
        volatile uint64_t *val;
        volatile int *turn;
        int count;
    } t_arg = { &mtx, &cv, &shared_val, &turn, PING_PONG_COUNT };

    void *worker_ping(void *p) {
        struct ThreadArg *a = (struct ThreadArg *)p;
        for (int i = 0; i < a->count; ++i) {
            pthread_mutex_lock(a->mtx);
            while (*(a->turn) != 1) {
                pthread_cond_wait(a->cv, a->mtx);
            }
            (*(a->val))++;
            *(a->turn) = 0;
            pthread_cond_signal(a->cv);
            pthread_mutex_unlock(a->mtx);
        }
        return NULL;
    }

    pthread_t worker_tid;
    start = get_time_ns();
    pthread_create(&worker_tid, NULL, worker_ping, &t_arg);

    for (int i = 0; i < PING_PONG_COUNT; ++i) {
        pthread_mutex_lock(&mtx);
        while (turn != 0) {
            pthread_cond_wait(&cv, &mtx);
        }
        shared_val++;
        turn = 1;
        pthread_cond_signal(&cv);
        pthread_mutex_unlock(&mtx);
    }
    pthread_join(worker_tid, NULL);
    uint64_t thread_time = get_time_ns() - start;
    double thread_latency_us = (double)thread_time / (PING_PONG_COUNT * 2 * 1000.0);

    printf("  Міжпроцесний обмін (Pipe IPC):     сер. затримка = %5.2f мкс на повідомлення\n", pipe_latency_us);
    printf("  Спільна пам'ять (Mutex + CondVar): сер. затримка = %5.2f мкс на повідомлення\n", thread_latency_us);
    printf("  -> Спільна пам'ять у %.1fx швидша за системні пайпи\n\n", pipe_latency_us / thread_latency_us);
}

// ── ТЕСТ 3: Демонстрація зони ураження збою (Blast Radius) ────────────────
static void test_fault_isolation(void) {
    printf("=== ТЕСТ 3: Демонстрація ізоляції збоїв (SIGSEGV) ===\n");

    // 1. Збій у дочірньому процесі
    pid_t pid = fork();
    if (pid == 0) {
        printf("  [Дочірній процес] Навмисний запис за покажчиком NULL...\n");
        volatile int *bad_ptr = NULL;
        *bad_ptr = 42; // Викликає SIGSEGV
        _exit(0);
    } else {
        int status = 0;
        waitpid(pid, &status, 0);
        if (WIFSIGNALED(status)) {
            printf("  [Батьківський процес] Дочірній процес упав від сигналу %d (%s).\n",
                   WTERMSIG(status), strsignal(WTERMSIG(status)));
            printf("  [Батьківський процес] Батько живий і продовжує роботу! Ізоляція спрацювала.\n");
        }
    }
    printf("  -> У багатопотоковій моделі аналогічний segfault убив би всю програму повністю.\n\n");
}

int main(void) {
    printf("=================================================================\n");
    printf("  БЕНЧМАРК: ПРОЦЕСИ ПРОТИ ПОТОКІВ НА LINUX (C / POSIX)\n");
    printf("=================================================================\n\n");

    long base_rss = get_rss_kb();
    printf("Базовий обсяг RSS процесу: %ld КБ\n\n", base_rss);

    test_creation_latency();
    test_ipc_vs_shared_mem();
    test_fault_isolation();

    return 0;
}
