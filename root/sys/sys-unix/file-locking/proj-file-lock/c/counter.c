/* counter.c — кілька процесів безпечно збільшують лічильник у файлі. */
#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

/* Реалізацію цих двох функцій дає окремий файл — саме нею
   й різняться три версії програми.                                 */
int lock_take(int fd);
int lock_drop(int fd);

/* pread має право повернути МЕНШЕ, ніж просили, і має право
   повернутися ні з чим, бо його перервав сигнал. Ні те, ні те
   не є помилкою — тому одного виклику ніколи не досить.            */
static ssize_t pread_all(int fd, void *buf, size_t len, off_t off)
{
    size_t got = 0;
    while (got < len) {
        ssize_t n = pread(fd, (char *) buf + got, len - got,
                          off + (off_t) got);
        if (n < 0) {
            if (errno == EINTR) continue;
            return -1;
        }
        if (n == 0) break;             /* кінець файлу: він просто коротший */
        got += (size_t) n;
    }
    return (ssize_t) got;
}

static int pwrite_all(int fd, const void *buf, size_t len, off_t off)
{
    size_t done = 0;
    while (done < len) {
        ssize_t n = pwrite(fd, (const char *) buf + done, len - done,
                           off + (off_t) done);
        if (n < 0) {
            if (errno == EINTR) continue;
            return -1;
        }
        if (n == 0) { errno = EIO; return -1; }
        done += (size_t) n;
    }
    return 0;
}

static int write_all(int fd, const void *buf, size_t len)
{
    size_t done = 0;
    while (done < len) {
        ssize_t n = write(fd, (const char *) buf + done, len - done);
        if (n < 0) {
            if (errno == EINTR) continue;
            return -1;
        }
        done += (size_t) n;
    }
    return 0;
}
