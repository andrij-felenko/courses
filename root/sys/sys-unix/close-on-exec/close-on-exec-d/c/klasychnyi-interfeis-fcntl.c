#include <fcntl.h>
#include <unistd.h>

int set_cloexec(int fd) {
    int flags = fcntl(fd, F_GETFD);
    if (flags == -1)
        return -1;
    
    return fcntl(fd, F_SETFD, flags | FD_CLOEXEC);
}
