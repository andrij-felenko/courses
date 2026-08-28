#include <stdio.h>
#include <sys/ioctl.h>
#include <linux/input.h>

int grab_device(int fd, int enable) {
    if (ioctl(fd, EVIOCGRAB, enable ? 1 : 0) < 0) {
        perror("Помилка виконання EVIOCGRAB");
        return -1;
    }
    return 0;
}
