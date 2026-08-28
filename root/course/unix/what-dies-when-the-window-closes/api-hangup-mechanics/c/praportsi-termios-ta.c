#include <termios.h>
#include <unistd.h>
#include <stdio.h>

int enable_hangup_on_close(int fd) {
    struct termios tty;
    if (tcgetattr(fd, &tty) < 0) {
        perror("tcgetattr");
        return -1;
    }
    tty.c_cflag |= HUPCL; /* Hangup on last close */
    if (tcsetattr(fd, TCSANOW, &tty) < 0) {
        perror("tcsetattr");
        return -1;
    }
    return 0;
}
