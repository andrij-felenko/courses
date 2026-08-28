/* uevent_monitor.c — Системний монітор подій ядра Linux на мові C */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <poll.h>
#include <signal.h>
#include <sys/socket.h>
#include <linux/netlink.h>

#define UEVENT_BUFFER_SIZE 16384
#define SOCKET_RECV_BUFFER (2 * 1024 * 1024) /* 2 МБ для запобігання ENOBUFS */

static volatile sig_atomic_t g_stop = 0;

static void handle_signal(int sig)
{
    (void)sig;
    g_stop = 1;
}

/* Структура для збереження покажчиків на витягнуті параметри події */
struct uevent_fields {
    const char *action;
    const char *devpath;
    const char *subsystem;
    const char *devname;
    const char *modalias;
    const char *seqnum;
    const char *major;
    const char *minor;
    const char *driver;
};

static void parse_uevent_buffer(const char *buf, ssize_t len, struct uevent_fields *fields)
{
    fields->action = "N/A";
    fields->devpath = "N/A";
    fields->subsystem = "N/A";
    fields->devname = NULL;
    fields->modalias = NULL;
    fields->seqnum = "N/A";
    fields->major = NULL;
    fields->minor = NULL;
    fields->driver = NULL;

    /* Перший рядок у пакеті — заголовок вигляду "add@/devices/..." */
    const char *header = buf;
    size_t header_len = strlen(header);
    const char *ptr = buf + header_len + 1;
    const char *end = buf + len;

    /* Ітеруємося по нуль-термінованих рядках KEY=VALUE */
    while (ptr < end && *ptr != '\0') {
        if (strncmp(ptr, "ACTION=", 7) == 0) {
            fields->action = ptr + 7;
        } else if (strncmp(ptr, "DEVPATH=", 8) == 0) {
            fields->devpath = ptr + 8;
        } else if (strncmp(ptr, "SUBSYSTEM=", 10) == 0) {
            fields->subsystem = ptr + 10;
        } else if (strncmp(ptr, "DEVNAME=", 8) == 0) {
            fields->devname = ptr + 8;
        } else if (strncmp(ptr, "MODALIAS=", 9) == 0) {
            fields->modalias = ptr + 9;
        } else if (strncmp(ptr, "SEQNUM=", 7) == 0) {
            fields->seqnum = ptr + 7;
        } else if (strncmp(ptr, "MAJOR=", 6) == 0) {
            fields->major = ptr + 6;
        } else if (strncmp(ptr, "MINOR=", 6) == 0) {
            fields->minor = ptr + 6;
        } else if (strncmp(ptr, "DRIVER=", 7) == 0) {
            fields->driver = ptr + 7;
        }

        /* Переходимо до наступного рядка за нульовим байтом */
        ptr += strlen(ptr) + 1;
    }
}

static void print_uevent(const struct uevent_fields *f)
{
    printf("────────────────────────────────────────────────────────────────\n");
    printf("[UEVENT #%-6s] ДІЯ: %-8s | ПІДСИСТЕМА: %s\n", f->seqnum, f->action, f->subsystem);
    printf("  Шлях у sysfs:  /sys%s\n", f->devpath);

    if (f->devname) {
        if (f->major && f->minor) {
            printf("  Нода у /dev:   /dev/%s (major:minor = %s:%s)\n", f->devname, f->major, f->minor);
        } else {
            printf("  Нода у /dev:   /dev/%s\n", f->devname);
        }
    }

    if (f->driver) {
        printf("  Драйвер ядра:  %s\n", f->driver);
    }

    if (f->modalias) {
        printf("  MODALIAS:      %s\n", f->modalias);
    }
}

int main(void)
{
    struct sigaction sa_sig;
    memset(&sa_sig, 0, sizeof(sa_sig));
    sa_sig.sa_handler = handle_signal;
    sigaction(SIGINT, &sa_sig, NULL);
    sigaction(SIGTERM, &sa_sig, NULL);

    int sock_fd = socket(PF_NETLINK, SOCK_RAW, NETLINK_KOBJECT_UEVENT);
    if (sock_fd < 0) {
        perror("Помилка створення сокета Netlink");
        return EXIT_FAILURE;
    }

    /* Встановлюємо розмір буфера прийому ядра */
    int buf_size = SOCKET_RECV_BUFFER;
    if (setsockopt(sock_fd, SOL_SOCKET, SO_RCVBUF, &buf_size, sizeof(buf_size)) < 0) {
        perror("Попередження: не вдалося встановити SO_RCVBUF");
    }

    struct sockaddr_nl sa;
    memset(&sa, 0, sizeof(sa));
    sa.nl_family = AF_NETLINK;
    sa.nl_pid = 0;       /* 0 дозволяє ядру призначити власний унікальний ID */
    sa.nl_groups = 1;   /* 1 — багатоадресна група подій kobject ядра */

    if (bind(sock_fd, (struct sockaddr *)&sa, sizeof(sa)) < 0) {
        perror("Помилка прив'язки bind() до групи Netlink");
        close(sock_fd);
        return EXIT_FAILURE;
    }

    printf("================================================================\n");
    printf(" Монітор подій Netlink uevent запущено (Ctrl+C для виходу)\n");
    printf(" Очікування повідомлень ядра про під'єднання пристроїв...\n");
    printf("================================================================\n");

    char buffer[UEVENT_BUFFER_SIZE];
    struct pollfd pfd;
    pfd.fd = sock_fd;
    pfd.events = POLLIN;

    while (!g_stop) {
        int ret = poll(&pfd, 1, 500); /* 500 мс таймаут для перевірки g_stop */
        if (ret < 0) {
            if (errno == EINTR)
                continue;
            perror("Помилка опитування poll()");
            break;
        }
        if (ret == 0)
            continue;

        if (pfd.revents & POLLIN) {
            ssize_t len = recv(sock_fd, buffer, sizeof(buffer) - 1, MSG_DONTWAIT);
            if (len < 0) {
                if (errno == EINTR || errno == EAGAIN || errno == EWOULDBLOCK)
                    continue;
                if (errno == ENOBUFS) {
                    fprintf(stderr, "УВАГА: переповнення буфера сокета (ENOBUFS). Частину подій втрачено.\n");
                    continue;
                }
                perror("Помилка виклику recv()");
                break;
            }

            if (len == 0)
                continue;

            buffer[len] = '\0';
            struct uevent_fields fields;
            parse_uevent_buffer(buffer, len, &fields);
            print_uevent(&fields);
            fflush(stdout);
        }
    }

    printf("\nЗавершення роботи монітора uevent. Закриття сокета.\n");
    close(sock_fd);
    return EXIT_SUCCESS;
}
