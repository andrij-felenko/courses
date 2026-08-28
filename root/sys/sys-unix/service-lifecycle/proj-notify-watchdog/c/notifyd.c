/* notifyd.c — служба Type=notify без libsystemd: READY=1 після listen,
   WATCHDOG=1 з того самого циклу, що робить роботу. */
#define _GNU_SOURCE
#include <errno.h>
#include <netinet/in.h>
#include <poll.h>
#include <signal.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <time.h>
#include <unistd.h>

static volatile sig_atomic_t stop_requested = 0;

static void on_terminate(int sig) { (void) sig; stop_requested = 1; }

/* ── Увесь протокол sd_notify: одна датаграма з рядками КЛЮЧ=значення. ── */
static int notify(const char *msg)
{
    const char *path = getenv("NOTIFY_SOCKET");
    if (!path || !*path)
        return 0;                       /* запустили не менеджером — мовчимо */

    struct sockaddr_un addr;
    memset(&addr, 0, sizeof addr);
    addr.sun_family = AF_UNIX;

    size_t len = strlen(path);
    if (len >= sizeof addr.sun_path) {
        errno = ENAMETOOLONG;
        return -1;
    }
    memcpy(addr.sun_path, path, len);

    socklen_t alen;
    if (addr.sun_path[0] == '@') {      /* абстрактний простір імен ядра */
        addr.sun_path[0] = '\0';
        alen = (socklen_t) (offsetof(struct sockaddr_un, sun_path) + len);
    } else {                            /* звичайний шлях у файловій системі */
        alen = (socklen_t) (offsetof(struct sockaddr_un, sun_path) + len + 1);
    }

    int fd = socket(AF_UNIX, SOCK_DGRAM | SOCK_CLOEXEC, 0);
    if (fd < 0)
        return -1;

    ssize_t n = sendto(fd, msg, strlen(msg), MSG_NOSIGNAL,
                       (struct sockaddr *) &addr, alen);
    int saved = errno;
    close(fd);
    errno = saved;
    return n < 0 ? -1 : 0;
}

/* Термін сторожового таймера в мікросекундах; 0 — сторожа немає.
   Змінна могла дістатися нам у спадок від предка — звіряємо номер процесу. */
static uint64_t watchdog_usec(void)
{
    const char *owner = getenv("WATCHDOG_PID");
    const char *usec  = getenv("WATCHDOG_USEC");

    if (owner && strtol(owner, NULL, 10) != (long) getpid())
        return 0;
    if (!usec)
        return 0;
    return strtoull(usec, NULL, 10);
}

static uint64_t now_ms(void)
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);   /* монотонний: переведення годинника не збиває */
    return (uint64_t) ts.tv_sec * 1000 + (uint64_t) ts.tv_nsec / 1000000;
}

/* Корисна робота: прийняти з'єднання, відповісти, закрити. */
static int serve_one(int srv)
{
    int c = accept4(srv, NULL, NULL, SOCK_CLOEXEC);
    if (c < 0)
        return 0;

    char buf[256];
    ssize_t n = recv(c, buf, sizeof buf, 0);
    if (n > 0)
        send(c, buf, (size_t) n, MSG_NOSIGNAL);
    close(c);
    return 1;
}

int main(void)
{
    struct sigaction sa;
    memset(&sa, 0, sizeof sa);
    sa.sa_handler = on_terminate;
    sigemptyset(&sa.sa_mask);
    sigaction(SIGTERM, &sa, NULL);   /* БЕЗ SA_RESTART: poll має повернутися з EINTR */
    sigaction(SIGINT,  &sa, NULL);
    signal(SIGPIPE, SIG_IGN);        /* інакше запис у закрите з'єднання вб'є службу */

    int srv = socket(AF_INET, SOCK_STREAM | SOCK_CLOEXEC, 0);
    int one = 1;
    setsockopt(srv, SOL_SOCKET, SO_REUSEADDR, &one, sizeof one);

    struct sockaddr_in a;
    memset(&a, 0, sizeof a);
    a.sin_family      = AF_INET;
    a.sin_port        = htons(9100);
    a.sin_addr.s_addr = htonl(INADDR_LOOPBACK);

    if (bind(srv, (struct sockaddr *) &a, sizeof a) < 0 || listen(srv, 64) < 0) {
        perror("bind/listen");
        return 1;                    /* READY=1 не було — менеджер бачить невдалий старт */
    }

    /* Аж ТЕПЕР порт слухається: залежні юніти можуть стартувати. */
    if (notify("READY=1\nSTATUS=слухаю 127.0.0.1:9100\n") < 0)
        perror("notify");

    uint64_t period_ms = watchdog_usec() / 2000;   /* половина терміну, мкс → мс */
    uint64_t next_ping = now_ms() + period_ms;
    uint64_t served    = 0;

    while (!stop_requested) {
        int timeout = -1;
        if (period_ms) {
            uint64_t now = now_ms();
            timeout = now >= next_ping ? 0 : (int) (next_ping - now);
        }

        struct pollfd pfd = { .fd = srv, .events = POLLIN };
        int r = poll(&pfd, 1, timeout);
        if (r < 0 && errno != EINTR)
            break;
        if (r > 0 && (pfd.revents & POLLIN))
            served += serve_one(srv);

        /* Ознака життя йде ЗВІДСИ — з циклу, що робить роботу. */
        if (period_ms && now_ms() >= next_ping) {
            char buf[96];
            snprintf(buf, sizeof buf,
                     "WATCHDOG=1\nSTATUS=обслужено з'єднань: %llu\n",
                     (unsigned long long) served);
            notify(buf);
            next_ping = now_ms() + period_ms;
        }
    }

    notify("STOPPING=1\nSTATUS=закриваю сокет\n");
    close(srv);
    return 0;                        /* чистий вихід: перезапуску не буде */
}
