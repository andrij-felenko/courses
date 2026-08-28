#include <unistd.h>
#include <stdio.h>
#include <errno.h>

int set_foreground_group(int fd, pid_t pgrp) {
    if (tcsetpgrp(fd, pgrp) < 0) {
        perror("tcsetpgrp");
        return -1;
    }
    return 0;
}
