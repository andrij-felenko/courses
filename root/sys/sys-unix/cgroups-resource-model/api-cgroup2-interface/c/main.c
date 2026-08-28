#include <errno.h>
#include <fcntl.h>
#include <poll.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>

int main(void)
{
    /* «розбуди мене, якщо за будь-яку секунду група простояла
       через брак пам'яті понад 150 мс» */
    int fd = open("/sys/fs/cgroup/build/memory.pressure", O_RDWR | O_NONBLOCK);
    if (fd < 0) { perror("open"); return 1; }

    const char *trigger = "some 150000 1000000";
    if (write(fd, trigger, strlen(trigger)) < 0) { perror("write"); return 1; }

    struct pollfd pfd = { .fd = fd, .events = POLLPRI };
    for (;;) {
        if (poll(&pfd, 1, -1) < 0) {
            if (errno == EINTR) continue;      /* сигнал — просто повторити */
            perror("poll"); return 1;
        }
        if (pfd.revents & POLLERR) break;      /* групу видалили */

        char buf[256];
        ssize_t n = pread(fd, buf, sizeof buf - 1, 0);
        if (n > 0) { buf[n] = '\0'; fputs(buf, stdout); }
    }
    close(fd);
    return 0;
}
