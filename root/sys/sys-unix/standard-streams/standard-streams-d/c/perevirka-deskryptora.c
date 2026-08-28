#include <stdio.h>
#include <unistd.h>
#include <termios.h>
#include <sys/ioctl.h>
#include <errno.h>

int check_if_terminal(int fd) {
    struct termios t;
    // Якщо ioctl успішний, дескриптор є терміналом
    if (ioctl(fd, TCGETS, &t) == 0) {
        return 1;
    }
    // Якщо повертається ENOTTY — це файл, pipe або сокет
    if (errno == ENOTTY) {
        return 0;
    }
    return 0;
}
