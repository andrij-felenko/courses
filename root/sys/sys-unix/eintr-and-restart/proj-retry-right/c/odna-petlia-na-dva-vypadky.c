#include <errno.h>
#include <unistd.h>

/* Читає len байтів. Менше — тільки якщо дані скінчилися. −1 — справжня помилка. */
ssize_t read_all(int fd, void *buf, size_t len) {
    char  *p    = buf;
    size_t done = 0;
    while (done < len) {
        ssize_t n = read(fd, p + done, len - done);
        if (n > 0)          { done += (size_t) n; continue; }  /* коротко — зсув */
        if (n == 0)         break;                             /* кінець даних   */
        if (errno == EINTR) continue;                          /* без зсуву      */
        return -1;
    }
    return (ssize_t) done;
}

ssize_t write_all(int fd, const void *buf, size_t len) {
    const char *p    = buf;
    size_t      done = 0;
    while (done < len) {
        ssize_t n = write(fd, p + done, len - done);
        if (n >= 0)         { done += (size_t) n; continue; }
        if (errno == EINTR) continue;
        return -1;
    }
    return (ssize_t) len;
}
