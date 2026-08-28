#include <fcntl.h>
#include <unistd.h>
#include <stdio.h>

/* Замінити вміст файлу path на buf/len так, щоб після будь-якого збою
   на диску лишався або цілий старий файл, або цілий новий. */
int replace_file(const char *dir, const char *name,
                 const void *buf, size_t len)
{
    char tmp[512], final[512];
    snprintf(tmp,   sizeof tmp,   "%s/.%s.tmp", dir, name);
    snprintf(final, sizeof final, "%s/%s",      dir, name);

    int fd = open(tmp, O_WRONLY | O_CREAT | O_TRUNC, 0644);
    if (fd < 0) return -1;

    const char *p = buf;
    size_t left = len;
    while (left > 0) {
        ssize_t n = write(fd, p, left);
        if (n < 0) { close(fd); return -1; }
        p += n; left -= (size_t)n;
    }

    if (fsync(fd) < 0) { close(fd); return -1; }   /* дані й розмір — на носії */
    if (close(fd) < 0) return -1;

    if (rename(tmp, final) < 0) return -1;         /* атомарна підміна імені */

    int dfd = open(dir, O_RDONLY | O_DIRECTORY);   /* сам каталог теж файл */
    if (dfd < 0) return -1;
    if (fsync(dfd) < 0) { close(dfd); return -1; } /* новий запис у ньому — на носії */
    return close(dfd);
}
