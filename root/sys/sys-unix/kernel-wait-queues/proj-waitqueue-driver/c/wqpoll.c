/* wqpoll.c — чекати на пристрій через poll(2) */
#include <fcntl.h>
#include <poll.h>
#include <stdio.h>
#include <unistd.h>

int main(void)
{
    struct pollfd p = { .events = POLLIN };
    char buf[64];

    p.fd = open("/dev/wqdemo", O_RDONLY | O_NONBLOCK);
    if (p.fd < 0) { perror("open"); return 1; }

    for (;;) {
        int r = poll(&p, 1, 5000);

        if (r < 0)  { perror("poll"); return 1; }
        if (r == 0) { puts("п'ять секунд тиші"); continue; }

        if (p.revents & POLLIN) {
            ssize_t n = read(p.fd, buf, sizeof(buf));

            if (n > 0) { fwrite(buf, 1, n, stdout); fflush(stdout); }
        }
    }
}
