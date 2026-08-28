#include <sys/socket.h>
#include <netinet/tcp.h>
#include <errno.h>
#include <stdio.h>
#include <string.h>

/* поставити цілочислену опцію й показати, що ядро справді взяло */
static int set_int_opt(int fd, int level, int name, int want, const char *label)
{
    if (setsockopt(fd, level, name, &want, sizeof want) < 0) {
        fprintf(stderr, "%s: setsockopt: %s\n", label, strerror(errno));
        return -1;
    }
    int got = 0;
    socklen_t len = sizeof got;
    if (getsockopt(fd, level, name, &got, &len) == 0 && got != want)
        fprintf(stderr, "%s: просив %d, ядро дало %d\n", label, want, got);
    return 0;
}

/* виклик */
set_int_opt(fd, IPPROTO_TCP, TCP_NODELAY, 1,      "TCP_NODELAY");
set_int_opt(fd, SOL_SOCKET,  SO_RCVBUF,   262144, "SO_RCVBUF");
