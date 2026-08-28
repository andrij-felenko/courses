/* Приклад атомарного запису конфігураційного файла на мові C */
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>

int save_config_atomic(const char *path, const char *data, size_t len) {
    char tmp_path[256];
    snprintf(tmp_path, sizeof(tmp_path), "%s.tmp", path);

    int fd = open(tmp_path, O_WRONLY | O_CREAT | O_TRUNC, 0644);
    if (fd < 0) return -1;

    if (write(fd, data, len) != (ssize_t)len) {
        close(fd);
        unlink(tmp_path);
        return -1;
    }

    if (fdatasync(fd) < 0) {
        close(fd);
        unlink(tmp_path);
        return -1;
    }
    close(fd);

    if (rename(tmp_path, path) < 0) {
        unlink(tmp_path);
        return -1;
    }

    char dir_path[256];
    snprintf(dir_path, sizeof(dir_path), "%s", path);
    char *slash = strrchr(dir_path, '/');
    if (slash) *slash = '\0';
    else snprintf(dir_path, sizeof(dir_path), ".");

    int dir_fd = open(dir_path, O_RDONLY | O_DIRECTORY);
    if (dir_fd >= 0) {
        fsync(dir_fd);
        close(dir_fd);
    }
    return 0;
}
