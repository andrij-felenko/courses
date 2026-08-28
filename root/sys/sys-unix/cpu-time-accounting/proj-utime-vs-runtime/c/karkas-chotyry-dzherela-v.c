#define _GNU_SOURCE
#include <fcntl.h>
#include <pthread.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/resource.h>
#include <sys/syscall.h>
#include <time.h>
#include <unistd.h>

/* Прочитати невеликий файл цілком. Повертає кількість байтів або −1. */
static ssize_t slurp(const char *path, char *buf, size_t cap)
{
    int fd = open(path, O_RDONLY | O_CLOEXEC);
    if (fd < 0) return -1;
    ssize_t n = read(fd, buf, cap - 1);
    close(fd);
    if (n < 0) return -1;
    buf[n] = '\0';
    return n;
}

/* Настінний монотонний час. Іде через vDSO, тобто НЕ входить у ядро й нічого
   не додає до системного часу — саме тому ним безпечно керувати спалюванням. */
static double now_mono(void)
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (double)ts.tv_sec + ts.tv_nsec / 1e9;
}

static double clk_tck(void)
{
    static double hz;
    if (hz == 0.0) hz = (double)sysconf(_SC_CLK_TCK);
    return hz;
}
