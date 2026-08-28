#include <errno.h>
#include <fcntl.h>
#include <linux/input.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/epoll.h>
#include <sys/stat.h>
#include <sys/sysmacros.h>
#include <unistd.h>
#include <systemd/sd-bus.h>
#include <systemd/sd-event.h>
#include <systemd/sd-login.h>

#define LOGIND    "org.freedesktop.login1"
#define MGR_PATH  "/org/freedesktop/login1"
#define MGR_IFACE "org.freedesktop.login1.Manager"
#define SES_IFACE "org.freedesktop.login1.Session"

typedef struct {
    sd_bus          *bus;
    sd_event        *event;
    sd_event_source *io;        /* стеження за пристроєм; NULL, поки пауза */
    char            *path;      /* об'єктний шлях НАШОГО сеансу */
    uint32_t         major, minor;
    int              fd;        /* робочий дескриптор пристрою, -1 — немає */
} Ctx;

static int on_readable(sd_event_source *s, int fd, uint32_t revents, void *userdata) {
    struct input_event ev[32];

    ssize_t n = read(fd, ev, sizeof ev);
    if (n < 0) {
        if (errno == EAGAIN)
            return 0;
        printf("read() → %s\n", strerror(errno));   /* ENODEV після відкликання */
        return 0;
    }
    for (size_t i = 0; i < (size_t) n / sizeof ev[0]; i++)
        if (ev[i].type == EV_KEY)
            printf("клавіша %u %s\n", ev[i].code,
                   ev[i].value ? "натиснуто" : "відпущено");
    return 0;
}

static int arm(Ctx *c) {
    c->io = sd_event_source_unref(c->io);
    return sd_event_add_io(c->event, &c->io, c->fd, EPOLLIN, on_readable, c);
}
