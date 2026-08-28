/* bench_sync.c — Вимірювання затримок системних викликів скидання кешу в C */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <time.h>
#include <errno.h>

#define BLOCK_SIZE 4096
#define ITERATIONS 1000

static double get_time_sec(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec + ts.tv_nsec * 1e-9;
}

static int run_test_fsync(const char *filename) {
    int fd = open(filename, O_WRONLY | O_CREAT | O_TRUNC, 0644);
    if (fd < 0) return -1;

    char buffer[BLOCK_SIZE];
    memset(buffer, 'A', BLOCK_SIZE);

    double start = get_time_sec();
    for (int i = 0; i < ITERATIONS; i++) {
        if (write(fd, buffer, BLOCK_SIZE) != BLOCK_SIZE) {
            close(fd);
            return -1;
        }
        if (fsync(fd) < 0) {
            close(fd);
            return -1;
        }
    }
    double elapsed = get_time_sec() - start;

    close(fd);
    printf("  [fsync]      %d ітерацій: %.4f с (%.2f ops/sec, %.3f мс/op)\n",
           ITERATIONS, elapsed, ITERATIONS / elapsed, (elapsed / ITERATIONS) * 1000.0);
    return 0;
}

static int run_test_fdatasync(const char *filename) {
    int fd = open(filename, O_WRONLY | O_CREAT | O_TRUNC, 0644);
    if (fd < 0) return -1;

    char buffer[BLOCK_SIZE];
    memset(buffer, 'B', BLOCK_SIZE);

    double start = get_time_sec();
    for (int i = 0; i < ITERATIONS; i++) {
        if (write(fd, buffer, BLOCK_SIZE) != BLOCK_SIZE) {
            close(fd);
            return -1;
        }
        if (fdatasync(fd) < 0) {
            close(fd);
            return -1;
        }
    }
    double elapsed = get_time_sec() - start;

    close(fd);
    printf("  [fdatasync]  %d ітерацій: %.4f с (%.2f ops/sec, %.3f мс/op)\n",
           ITERATIONS, elapsed, ITERATIONS / elapsed, (elapsed / ITERATIONS) * 1000.0);
    return 0;
}

static int run_test_sync_range(const char *filename) {
    int fd = open(filename, O_WRONLY | O_CREAT | O_TRUNC, 0644);
    if (fd < 0) return -1;

    char buffer[BLOCK_SIZE];
    memset(buffer, 'C', BLOCK_SIZE);

    double start = get_time_sec();
    off64_t offset = 0;
    for (int i = 0; i < ITERATIONS; i++) {
        if (write(fd, buffer, BLOCK_SIZE) != BLOCK_SIZE) {
            close(fd);
            return -1;
        }
        if (sync_file_range(fd, offset, BLOCK_SIZE,
                            SYNC_FILE_RANGE_WAIT_BEFORE |
                            SYNC_FILE_RANGE_WRITE |
                            SYNC_FILE_RANGE_WAIT_AFTER) < 0) {
            close(fd);
            return -1;
        }
        offset += BLOCK_SIZE;
    }
    double elapsed = get_time_sec() - start;

    close(fd);
    printf("  [sync_range] %d ітерацій: %.4f с (%.2f ops/sec, %.3f мс/op) [УВАГА: НЕ захищає від знеструмлення!]\n",
           ITERATIONS, elapsed, ITERATIONS / elapsed, (elapsed / ITERATIONS) * 1000.0);
    return 0;
}

static int run_test_odsync(const char *filename) {
    int fd = open(filename, O_WRONLY | O_CREAT | O_TRUNC | O_DSYNC, 0644);
    if (fd < 0) return -1;

    char buffer[BLOCK_SIZE];
    memset(buffer, 'D', BLOCK_SIZE);

    double start = get_time_sec();
    for (int i = 0; i < ITERATIONS; i++) {
        if (write(fd, buffer, BLOCK_SIZE) != BLOCK_SIZE) {
            close(fd);
            return -1;
        }
    }
    double elapsed = get_time_sec() - start;

    close(fd);
    printf("  [O_DSYNC]    %d ітерацій: %.4f с (%.2f ops/sec, %.3f мс/op)\n",
           ITERATIONS, elapsed, ITERATIONS / elapsed, (elapsed / ITERATIONS) * 1000.0);
    return 0;
}

int main(void) {
    printf("=== Бенчмарк скидання кешу (C) ===\n");
    const char *testfile = "sync_bench.tmp";

    if (run_test_fsync(testfile) < 0) perror("fsync failed");
    if (run_test_fdatasync(testfile) < 0) perror("fdatasync failed");
    if (run_test_sync_range(testfile) < 0) perror("sync_file_range failed");
    if (run_test_odsync(testfile) < 0) perror("O_DSYNC failed");

    unlink(testfile);
    return 0;
}
