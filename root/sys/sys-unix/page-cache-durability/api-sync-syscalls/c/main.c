#define _GNU_SOURCE
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>

/* Дописати len байтів у кінець журналу і зробити їх довговічними.
   Повертає 0 при успіху; −1 означає, що вміст журналу після останнього
   вдалого виклику вважається втраченим — повторювати НЕ можна. */
int wal_append(int fd, const void *buf, size_t len)
{
    const char *p = buf;
    size_t left = len;

    while (left > 0) {
        ssize_t n = write(fd, p, left);
        if (n < 0) {
            if (errno == EINTR) continue;   /* сигнал — це не відмова */
            return -1;
        }
        p += n;
        left -= (size_t)n;
    }

    /* Файл росте, тож fdatasync усе одно винесе новий розмір,
       але не чіпатиме часів — саме цього ми й хочемо. */
    while (fdatasync(fd) < 0) {
        if (errno == EINTR) continue;
        return -1;                          /* EIO/ENOSPC — відновлюємося, не повторюємо */
    }
    return 0;
}
