#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/stat.h>
#include <time.h>

#define ITERATIONS 1000000

static double measure_lookup(int dirfd, const char *filename, int iterations) {
    struct stat st;
    struct timespec start, end;

    clock_gettime(CLOCK_MONOTONIC, &start);
    for (int i = 0; i < iterations; ++i) {
        /* AT_SYMLINK_NOFOLLOW вимикає зайве розкриття symlinks */
        fstatat(dirfd, filename, &st, AT_SYMLINK_NOFOLLOW);
    }
    clock_gettime(CLOCK_MONOTONIC, &end);

    double total_sec = (end.tv_sec - start.tv_sec) +
                       (end.tv_nsec - start.tv_nsec) * 1e-9;
    return (total_sec / iterations) * 1e9; /* наносекунди на виклик */
}

int main(int argc, char **argv) {
    const char *test_dir = "/tmp/dcache_bench";
    char existing_file[256];
    char missing_file[256];

    mkdir(test_dir, 0755);
    snprintf(existing_file, sizeof(existing_file), "present_file.txt");
    snprintf(missing_file, sizeof(missing_file), "absent_file.txt");

    int dirfd = open(test_dir, O_RDONLY | O_DIRECTORY);
    if (dirfd < 0) {
        perror("open test_dir");
        return 1;
    }

    /* Створюємо один реальний файл */
    int fd = openat(dirfd, existing_file, O_CREAT | O_WRONLY | O_TRUNC, 0644);
    if (fd >= 0) close(fd);

    printf("=== Бенчмарк швидкодії dcache (ітерацій: %d) ===\n", ITERATIONS);

    /* 1. Гарячий позитивний хіт */
    double t_pos = measure_lookup(dirfd, existing_file, ITERATIONS);
    printf("1. Positive dentry hit (існуючий файл):       %6.2f нс / виклик\n", t_pos);

    /* Прогріваємо негативний dentry (одноразове звернення створює negative dentry) */
    struct stat dummy;
    fstatat(dirfd, missing_file, &dummy, AT_SYMLINK_NOFOLLOW);

    /* 2. Гарячий негативний хіт */
    double t_neg = measure_lookup(dirfd, missing_file, ITERATIONS);
    printf("2. Negative dentry hit (відсутній, кешований): %6.2f нс / виклик\n", t_neg);

    printf("\nДля тестування холодного промаху виконайте: sync && echo 2 | sudo tee /proc/sys/vm/drop_caches\n");

    close(dirfd);
    unlinkat(AT_FDCWD, "/tmp/dcache_bench/present_file.txt", 0);
    rmdir(test_dir);
    return 0;
}
