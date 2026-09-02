// Демон, якого systemd тримає трьома контрактами одразу:
//   * слухаючий сокет приходить від менеджера (сокетна активація);
//   * готовність оголошується самою службою (Type=notify, READY=1);
//   * працездатність підтверджується пульсом WATCHDOG=1 кожні WatchdogSec/2.
// Усе це живе в одному циклі epoll: сокет, сигнали й таймер сторожа — просто
// три дескриптори, з яких читають події.
#define _GNU_SOURCE

#include "listen_fds.h"

#include <systemd/sd-daemon.h>

#include <errno.h>
#include <fcntl.h>
#include <signal.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <sys/epoll.h>
#include <sys/signalfd.h>
#include <sys/socket.h>
#include <sys/timerfd.h>
#include <time.h>
#include <unistd.h>

#define MAX_CLIENTS 16
#define REQUEST_MAX 512
#define STUCK_LIMIT_NS 30000000000ULL   // недочитаний запит довше 30 с = зупинений цикл
#define DEFAULT_SOCKET_PATH "/run/app-worker/worker.sock"

struct client {
    int fd;                     // -1 — слот вільний
    size_t len;                 // скільки байтів запиту вже накопичено
    uint64_t first_byte_ns;     // коли прийшов перший байт незавершеного запиту
    char buf[REQUEST_MAX];
};

struct server {
    struct listen_socket listen;
    int epoll_fd;
    int signal_fd;
    int timer_fd;               // -1, якщо WatchdogSec= не задано
    uint64_t ping_usec;
    struct client clients[MAX_CLIENTS];
    unsigned accepted_total;
    unsigned rejected_total;
    uint64_t started_ns;
    bool running;
};

static uint64_t now_ns(void)
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (uint64_t)ts.tv_sec * 1000000000ULL + (uint64_t)ts.tv_nsec;
}

static int epoll_add(int epoll_fd, int fd)
{
    struct epoll_event ev;
    memset(&ev, 0, sizeof ev);
    ev.events = EPOLLIN;
    ev.data.fd = fd;
    return epoll_ctl(epoll_fd, EPOLL_CTL_ADD, fd, &ev) < 0 ? -errno : 0;
}

// Сигнали завершення забираємо дескриптором, а не обробником: у циклі подій
// вони стають звичайною подією й не рвуть системний виклик посеред роботи.
static int signal_fd_open(void)
{
    sigset_t mask;
    int fd;

    sigemptyset(&mask);
    sigaddset(&mask, SIGTERM);
    sigaddset(&mask, SIGINT);

    // Блокування обов'язкове: інакше типова дія вб'є процес раніше, ніж ми
    // прочитаємо подію з signalfd.
    if (sigprocmask(SIG_BLOCK, &mask, NULL) < 0)
        return -errno;

    fd = signalfd(-1, &mask, SFD_NONBLOCK | SFD_CLOEXEC);
    return fd < 0 ? -errno : fd;
}

// Повертає 1, якщо нагляд увімкнено (таймер створено), 0 — якщо ні, або -errno.
static int watchdog_timer_open(int *out_fd, uint64_t *out_ping_usec)
{
    struct itimerspec its;
    uint64_t usec = 0, ping;
    int fd, saved, r;

    *out_fd = -1;
    *out_ping_usec = 0;

    r = sd_watchdog_enabled(0, &usec);
    if (r < 0)
        return r;
    if (r == 0 || usec == 0)
        return 0;   // WatchdogSec= не задано — служба працює без пульсу

    // Половина інтервалу — запас на затримки планувальника під навантаженням.
    ping = usec / 2;
    if (ping < 1000)
        ping = 1000;

    fd = timerfd_create(CLOCK_MONOTONIC, TFD_NONBLOCK | TFD_CLOEXEC);
    if (fd < 0)
        return -errno;

    memset(&its, 0, sizeof its);
    its.it_interval.tv_sec = (time_t)(ping / 1000000ULL);
    its.it_interval.tv_nsec = (long)((ping % 1000000ULL) * 1000ULL);
    its.it_value = its.it_interval;

    if (timerfd_settime(fd, 0, &its, NULL) < 0) {
        saved = errno;
        close(fd);
        return -saved;
    }

    *out_fd = fd;
    *out_ping_usec = ping;
    return 1;
}

static struct client *client_slot(struct server *s)
{
    for (int i = 0; i < MAX_CLIENTS; i++)
        if (s->clients[i].fd < 0)
            return &s->clients[i];
    return NULL;
}

static struct client *client_by_fd(struct server *s, int fd)
{
    for (int i = 0; i < MAX_CLIENTS; i++)
        if (s->clients[i].fd == fd)
            return &s->clients[i];
    return NULL;
}

static void client_close(struct server *s, struct client *c)
{
    epoll_ctl(s->epoll_fd, EPOLL_CTL_DEL, c->fd, NULL);
    close(c->fd);
    c->fd = -1;
    c->len = 0;
    c->first_byte_ns = 0;
}

// Повертає true, якщо з'єднання лишилося живим.
static bool client_reply(struct server *s, struct client *c, const char *text)
{
    size_t len = strlen(text);
    ssize_t written = write(c->fd, text, len);

    if (written < 0 || (size_t)written != len) {
        // Відповіді короткі, часткового запису на них не буває. Якщо він стався —
        // клієнт зник або переповнив свій буфер, тримати з'єднання нема сенсу.
        fprintf(stderr, SD_WARNING "клієнт fd=%d не прийняв відповідь: %s\n",
                c->fd, strerror(errno));
        client_close(s, c);
        return false;
    }
    return true;
}

static bool handle_request(struct server *s, struct client *c, const char *line)
{
    char out[256];

    if (strcmp(line, "PING") == 0)
        return client_reply(s, c, "PONG\n");

    if (strcmp(line, "STATUS") == 0) {
        snprintf(out, sizeof out,
                 "OK uptime=%llus accepted=%u rejected=%u watchdog=%s\n",
                 (unsigned long long)((now_ns() - s->started_ns) / 1000000000ULL),
                 s->accepted_total, s->rejected_total,
                 s->timer_fd >= 0 ? "on" : "off");
        return client_reply(s, c, out);
    }

    if (strcmp(line, "QUIT") == 0) {
        if (client_reply(s, c, "BYE\n"))
            client_close(s, c);
        return false;
    }

    return client_reply(s, c, "ERR unknown command\n");
}

static void on_client_readable(struct server *s, struct client *c)
{
    for (;;) {
        ssize_t got;

        if (c->len == sizeof c->buf) {
            // Рядок без переводу довший за буфер: або чужий протокол, або спроба
            // забити нам пам'ять. Обриваємо, поки буфер один на з'єднання.
            fprintf(stderr, SD_WARNING "запит клієнта fd=%d довший за %zu байтів\n",
                    c->fd, sizeof c->buf);
            client_close(s, c);
            return;
        }

        got = read(c->fd, c->buf + c->len, sizeof c->buf - c->len);
        if (got < 0) {
            if (errno == EINTR)
                continue;
            if (errno == EAGAIN || errno == EWOULDBLOCK)
                return;   // усе прочитано, чекаємо наступної події
            fprintf(stderr, SD_WARNING "read(fd=%d): %s\n", c->fd, strerror(errno));
            client_close(s, c);
            return;
        }
        if (got == 0) {
            client_close(s, c);   // клієнт закрив свій бік
            return;
        }

        if (c->len == 0)
            c->first_byte_ns = now_ns();
        c->len += (size_t)got;

        // Розбираємо всі повні рядки, що вже лежать у буфері.
        for (;;) {
            char line[REQUEST_MAX];
            char *nl = memchr(c->buf, '\n', c->len);
            size_t line_len, rest;

            if (nl == NULL)
                break;

            line_len = (size_t)(nl - c->buf);
            memcpy(line, c->buf, line_len);
            line[line_len] = '\0';
            if (line_len > 0 && line[line_len - 1] == '\r')
                line[line_len - 1] = '\0';

            rest = c->len - line_len - 1;
            memmove(c->buf, nl + 1, rest);
            c->len = rest;
            c->first_byte_ns = rest > 0 ? now_ns() : 0;

            if (!handle_request(s, c, line))
                return;   // з'єднання вже закрите, слот більше не наш
        }
    }
}

static void on_listen_readable(struct server *s)
{
    for (;;) {
        struct client *c;
        int fd = accept4(s->listen.fd, NULL, NULL, SOCK_NONBLOCK | SOCK_CLOEXEC);

        if (fd < 0) {
            if (errno == EINTR || errno == ECONNABORTED)
                continue;   // клієнт передумав між connect() і accept()
            if (errno == EAGAIN || errno == EWOULDBLOCK)
                return;
            if (errno == EMFILE || errno == ENFILE) {
                // З'єднання лишається в черзі backlog: заберемо його, коли
                // звільниться дескриптор. Це не привід падати.
                fprintf(stderr, SD_ERR "вичерпано ліміт дескрипторів: %s\n",
                        strerror(errno));
                return;
            }
            fprintf(stderr, SD_ERR "accept4: %s\n", strerror(errno));
            return;
        }

        c = client_slot(s);
        if (c == NULL) {
            ssize_t ignored = write(fd, "ERR busy\n", 9);
            (void)ignored;
            close(fd);
            s->rejected_total++;
            fprintf(stderr, SD_WARNING "усі %d слотів зайнято — відмовляємо клієнтові\n",
                    MAX_CLIENTS);
            continue;
        }

        if (epoll_add(s->epoll_fd, fd) < 0) {
            fprintf(stderr, SD_ERR "epoll_ctl(ADD, %d): %s\n", fd, strerror(errno));
            close(fd);
            continue;
        }

        c->fd = fd;
        c->len = 0;
        c->first_byte_ns = 0;
        s->accepted_total++;
    }
}

// Самодіагностика перед пульсом. Сенс сторожа саме в цьому: пінг має означати
// «я обслуговую роботу», а не «мій таймер ще цокає».
static bool self_check(struct server *s)
{
    uint64_t now = now_ns();

    if (fcntl(s->listen.fd, F_GETFD) < 0) {
        fprintf(stderr, SD_ERR "слухаючий дескриптор утрачено: %s\n", strerror(errno));
        return false;
    }

    for (int i = 0; i < MAX_CLIENTS; i++) {
        const struct client *c = &s->clients[i];
        if (c->fd >= 0 && c->len > 0 && now - c->first_byte_ns > STUCK_LIMIT_NS) {
            fprintf(stderr, SD_ERR "запит клієнта fd=%d висить понад 30 с\n", c->fd);
            return false;
        }
    }
    return true;
}

static void on_watchdog_tick(struct server *s)
{
    uint64_t ticks = 0;
    int r;

    if (read(s->timer_fd, &ticks, sizeof ticks) != (ssize_t)sizeof ticks)
        return;

    if (!self_check(s)) {
        // Свідомо мовчимо: менеджер вичерпає WatchdogSec=, надішле SIGABRT
        // (звідки візьметься core dump зі станом усіх стеків) і перезапустить нас.
        fprintf(stderr, SD_ERR "самодіагностика не пройшла — пульс не надсилаємо\n");
        return;
    }

    r = sd_notify(0, "WATCHDOG=1");
    if (r < 0)
        fprintf(stderr, SD_ERR "sd_notify(WATCHDOG=1): %s\n", strerror(-r));
}

static void on_signal(struct server *s)
{
    struct signalfd_siginfo si;

    if (read(s->signal_fd, &si, sizeof si) != (ssize_t)sizeof si)
        return;

    fprintf(stderr, SD_INFO "сигнал %u — зупиняємось\n", si.ssi_signo);

    // STOPPING=1 переводить юніт у стан deactivating і знімає з нас вимогу
    // пульсу на час коректної зупинки.
    sd_notify(0, "STOPPING=1\nSTATUS=Завершуємо обслуговування\n");
    s->running = false;
}

int main(int argc, char *argv[])
{
    static struct server s;
    const char *socket_path = argc > 1 ? argv[1] : DEFAULT_SOCKET_PATH;
    struct epoll_event events[8];
    int r, status = 0;

    // Клієнт може зникнути посеред нашої відповіді; без цього ядро вб'є процес
    // сигналом SIGPIPE, і менеджер порахує це аварією служби.
    signal(SIGPIPE, SIG_IGN);

    s.epoll_fd = -1;
    s.signal_fd = -1;
    s.timer_fd = -1;
    s.listen.fd = -1;
    s.running = true;
    s.started_ns = now_ns();
    for (int i = 0; i < MAX_CLIENTS; i++)
        s.clients[i].fd = -1;

    r = listen_socket_acquire(socket_path, &s.listen);
    if (r < 0) {
        fprintf(stderr, SD_ERR "слухаючий сокет: %s\n", strerror(-r));
        return 1;
    }

    s.epoll_fd = epoll_create1(EPOLL_CLOEXEC);
    if (s.epoll_fd < 0) {
        fprintf(stderr, SD_ERR "epoll_create1: %s\n", strerror(errno));
        status = 1;
        goto out;
    }

    r = signal_fd_open();
    if (r < 0) {
        fprintf(stderr, SD_ERR "signalfd: %s\n", strerror(-r));
        status = 1;
        goto out;
    }
    s.signal_fd = r;

    r = watchdog_timer_open(&s.timer_fd, &s.ping_usec);
    if (r < 0) {
        fprintf(stderr, SD_ERR "сторожовий таймер: %s\n", strerror(-r));
        status = 1;
        goto out;
    }

    if (epoll_add(s.epoll_fd, s.listen.fd) < 0 ||
        epoll_add(s.epoll_fd, s.signal_fd) < 0 ||
        (s.timer_fd >= 0 && epoll_add(s.epoll_fd, s.timer_fd) < 0)) {
        fprintf(stderr, SD_ERR "epoll_ctl(ADD): %s\n", strerror(errno));
        status = 1;
        goto out;
    }

    fprintf(stderr, SD_INFO "сокет %s, пульс кожні %llu мкс\n",
            listen_source_name(s.listen.source), (unsigned long long)s.ping_usec);

    // Аж тепер юніт переходить у стан active: усе, що потрібно для роботи,
    // уже підняте, тож залежні служби стартують не в порожнечу.
    sd_notifyf(0, "READY=1\nSTATUS=Слухаю сокет (%s), клієнтів максимум %d\n",
               listen_source_name(s.listen.source), MAX_CLIENTS);

    while (s.running) {
        int n = epoll_wait(s.epoll_fd, events, (int)(sizeof events / sizeof events[0]), -1);
        if (n < 0) {
            if (errno == EINTR)
                continue;
            fprintf(stderr, SD_ERR "epoll_wait: %s\n", strerror(errno));
            status = 1;
            break;
        }

        for (int i = 0; i < n; i++) {
            int fd = events[i].data.fd;

            if (fd == s.listen.fd) {
                on_listen_readable(&s);
            } else if (fd == s.signal_fd) {
                on_signal(&s);
            } else if (fd == s.timer_fd) {
                on_watchdog_tick(&s);
            } else {
                struct client *c = client_by_fd(&s, fd);
                if (c != NULL)   // NULL, якщо слот закрили раніше в цьому ж пакеті подій
                    on_client_readable(&s, c);
            }
        }
    }

out:
    for (int i = 0; i < MAX_CLIENTS; i++)
        if (s.clients[i].fd >= 0)
            close(s.clients[i].fd);
    if (s.timer_fd >= 0)
        close(s.timer_fd);
    if (s.signal_fd >= 0)
        close(s.signal_fd);
    if (s.epoll_fd >= 0)
        close(s.epoll_fd);
    listen_socket_release(&s.listen);

    return status;
}
