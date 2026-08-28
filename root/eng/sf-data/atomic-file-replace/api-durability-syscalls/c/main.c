#define _GNU_SOURCE
#include <fcntl.h>
#include <unistd.h>
#include <stdio.h>

int write_via_tmpfile(const char *dir, const char *target, const void *buf, size_t len) {
    // Створення файлу без імені у просторі каталогу
    int fd = open(dir, O_TMPFILE | O_RDWR, 0600);
    if (fd < 0) return -1;

    // Запис та скидання на диск
    if (write(fd, buf, len) != (ssize_t)len || fsync(fd) != 0) {
        close(fd);
        return -1;
    }

    // Атомарне надання імені (прив'язка до dentry)
    char fd_path[64];
    snprintf(fd_path, sizeof(fd_path), "/proc/self/fd/%d", fd);
    int res = linkat(AT_FDCWD, fd_path, AT_FDCWD, target, AT_SYMLINK_FOLLOW);
    close(fd);
    return res;
}
