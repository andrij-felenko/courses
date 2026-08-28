#include <stdio.h>
#include <unistd.h>
#include <fcntl.h>
#include <string.h>

/* Читання поточного значення ліміту відкритих файлів ядра */
int get_kernel_max_files(long long *out_val) {
    int fd = open("/proc/sys/fs/file-max", O_RDONLY);
    if (fd < 0) {
        return -1;
    }

    char buf[64];
    ssize_t n = read(fd, buf, sizeof(buf) - 1);
    close(fd);

    if (n <= 0) {
        return -1;
    }

    buf[n] = '\0';
    if (sscanf(buf, "%lld", out_val) != 1) {
        return -1;
    }
    return 0;
}
