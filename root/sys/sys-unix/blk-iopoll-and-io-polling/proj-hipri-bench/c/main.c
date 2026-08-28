#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <time.h>
#include <sched.h>
#include <sys/uio.h>
#include <linux/fs.h>   /* RWF_HIPRI */
#include <liburing.h>

#define ALIGNMENT 4096
#define BLOCK_SIZE 4096
#define NUM_ITERATIONS 100000

static double get_time_us(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC_RAW, &ts);
    return (double)ts.tv_sec * 1e6 + (double)ts.tv_nsec / 1e3;
}

static void pin_to_cpu(int cpu_id) {
    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);
    CPU_SET(cpu_id, &cpuset);
    if (sched_setaffinity(0, sizeof(cpu_set_t), &cpuset) != 0) {
        perror("Не вдалося прив'язати потік до CPU");
        exit(1);
    }
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Використання: %s /dev/nvme0n1\n", argv[0]);
        return 1;
    }

    pin_to_cpu(1);

    int fd = open(argv[1], O_RDONLY | O_DIRECT);
    if (fd < 0) {
        perror("Помилка відкриття пристрою з O_DIRECT");
        return 1;
    }

    void *buf = NULL;
    if (posix_memalign(&buf, ALIGNMENT, BLOCK_SIZE) != 0) {
        perror("Помилка виділення вирівняного буфера");
        close(fd);
        return 1;
    }

    /* Тест 1: preadv2 з прапорцем RWF_HIPRI (Синхронний IO Polling) */
    struct iovec iov = { .iov_base = buf, .iov_len = BLOCK_SIZE };
    double start_time = get_time_us();

    for (int i = 0; i < NUM_ITERATIONS; i++) {
        off_t offset = (i % 1000) * BLOCK_SIZE;
        ssize_t ret = preadv2(fd, &iov, 1, offset, RWF_HIPRI);
        if (ret < 0) {
            perror("preadv2 RWF_HIPRI failed");
            break;
        }
    }

    double total_time = get_time_us() - start_time;
    printf("preadv2 (RWF_HIPRI): %.2f IOPS, середня затримка: %.2f мкс\n",
           (NUM_ITERATIONS / total_time) * 1e6, total_time / NUM_ITERATIONS);

    /* Тест 2: io_uring з прапорцем IORING_SETUP_IOPOLL (Асинхронний IO Polling) */
    struct io_uring ring;
    if (io_uring_queue_init(64, &ring, IORING_SETUP_IOPOLL) < 0) {
        fprintf(stderr, "Не вдалося ініціалізувати io_uring з IOPOLL\n");
        free(buf);
        close(fd);
        return 1;
    }

    start_time = get_time_us();
    for (int i = 0; i < NUM_ITERATIONS; i++) {
        off_t offset = (i % 1000) * BLOCK_SIZE;
        struct io_uring_sqe *sqe = io_uring_get_sqe(&ring);
        io_uring_prep_read(sqe, fd, buf, BLOCK_SIZE, offset);

        /* Відправляємо запит */
        io_uring_submit(&ring);

        /* Виконуємо активний поллінг завершення */
        struct io_uring_cqe *cqe;
        int ret = io_uring_wait_cqe(&ring, &cqe);
        if (ret < 0 || cqe->res < 0) {
            fprintf(stderr, "Помилка виконання io_uring cqe\n");
            break;
        }
        io_uring_cqe_seen(&ring, cqe);
    }

    total_time = get_time_us() - start_time;
    printf("io_uring (IOPOLL): %.2f IOPS, середня затримка: %.2f мкс\n",
           (NUM_ITERATIONS / total_time) * 1e6, total_time / NUM_ITERATIONS);

    io_uring_queue_exit(&ring);
    free(buf);
    close(fd);
    return 0;
}
