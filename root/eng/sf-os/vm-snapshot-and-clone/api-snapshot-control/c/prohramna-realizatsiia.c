#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/fs.h>
#include <errno.h>
#include <string.h>

int freeze_mountpoint(const char *mount_path) {
    int fd = open(mount_path, O_RDONLY | O_CLOEXEC);
    if (fd < 0) {
        fprintf(stderr, "Помилка відкриття шляху монтування %s: %s\n", 
                mount_path, strerror(errno));
        return -1;
    }

    if (ioctl(fd, FIFREEZE, 0) < 0) {
        fprintf(stderr, "Помилка виклику ioctl FIFREEZE для %s: %s\n", 
                mount_path, strerror(errno));
        close(fd);
        return -1;
    }

    return fd;
}

int thaw_mountpoint(int fd, const char *mount_path) {
    int result = 0;
    if (ioctl(fd, FITHAW, 0) < 0) {
        fprintf(stderr, "Критична помилка розморожування FITHAW для %s: %s\n", 
                mount_path, strerror(errno));
        result = -1;
    }
    close(fd);
    return result;
}
