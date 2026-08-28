/* bench_blk_mq.c — C-версія високопродуктивного тестового генератора */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <time.h>
#include <pthread.h>
#include <string.h>
#include <errno.h>

#define BLOCK_SIZE 4096
#define IO_COUNT 200000

struct thread_args {
    const char *dev_path;
    int thread_id;
    long total_ops;
    double elapsed_sec;
};

static double get_time_sec(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec + ts.tv_nsec / 1e9;
}

void *bench_worker(void *arg) {
    struct thread_args *targs = (struct thread_args *)arg;
    
    /* Відкриття пристрою в режимі O_DIRECT для обходу Page Cache */
    int fd = open(targs->dev_path, O_RDWR | O_DIRECT);
    if (fd < 0) {
        fprintf(stderr, "Помилка відкриття %s: %s\n", targs->dev_path, strerror(errno));
        pthread_exit(NULL);
    }

    /* Вирівнювання пам'яті за межею 4096 байт для O_DIRECT */
    void *buf = NULL;
    if (posix_memalign(&buf, BLOCK_SIZE, BLOCK_SIZE) != 0) {
        fprintf(stderr, "Помилка виділення вирівняної пам'яті\n");
        close(fd);
        pthread_exit(NULL);
    }
    memset(buf, 0x5A, BLOCK_SIZE);

    off_t offset = (off_t)targs->thread_id * BLOCK_SIZE * 10000;
    double t_start = get_time_sec();

    for (long i = 0; i < targs->total_ops; ++i) {
        ssize_t ret = pwrite(fd, buf, BLOCK_SIZE, offset);
        if (ret != BLOCK_SIZE) {
            fprintf(stderr, "Помилка pwrite на ітерації %ld: %s\n", i, strerror(errno));
            break;
        }
        offset += BLOCK_SIZE;
    }

    double t_end = get_time_sec();
    targs->elapsed_sec = t_end - t_start;

    free(buf);
    close(fd);
    pthread_exit(NULL);
}

int main(int argc, char *argv[]) {
    const char *dev = (argc > 1) ? argv[1] : "/dev/nullb0";
    int num_threads = (argc > 2) ? atoi(argv[2]) : 4;

    printf("=== Бенчмарк blk-mq на пристрої %s (%d потоків) ===\n", dev, num_threads);

    pthread_t threads[num_threads];
    struct thread_args targs[num_threads];

    double global_start = get_time_sec();

    for (int i = 0; i < num_threads; ++i) {
        targs[i].dev_path = dev;
        targs[i].thread_id = i;
        targs[i].total_ops = IO_COUNT;
        targs[i].elapsed_sec = 0.0;
        if (pthread_create(&threads[i], NULL, bench_worker, &targs[i]) != 0) {
            fprintf(stderr, "Помилка створення потоку %d\n", i);
            return 1;
        }
    }

    for (int i = 0; i < num_threads; ++i) {
        pthread_join(threads[i], NULL);
    }

    double global_end = get_time_sec();
    double total_elapsed = global_end - global_start;
    long total_io = (long)num_threads * IO_COUNT;
    double total_iops = total_io / total_elapsed;
    double total_mbps = (total_iops * BLOCK_SIZE) / (1024.0 * 1024.0);

    printf("Результати:\n");
    printf("  Виконано операцій  : %ld\n", total_io);
    printf("  Загальний час     : %.4f сек\n", total_elapsed);
    printf("  Продуктивність    : %.2f IOPS\n", total_iops);
    printf("  Пропускна здатність: %.2f MB/s\n", total_mbps);

    return 0;
}
