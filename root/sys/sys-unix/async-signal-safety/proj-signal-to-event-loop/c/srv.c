/* srv.c — cc -O2 -Wall -Wextra -o srv srv.c    (варіантові з signalfd на glibc до 2.34: додати -pthread) */
#define _GNU_SOURCE
#include <arpa/inet.h>
#include <errno.h>
#include <fcntl.h>
#include <netinet/in.h>
#include <poll.h>
#include <signal.h>
#include <string.h>
#include <sys/socket.h>
#include <unistd.h>

#define MAX_CONN   64
#define PORT       9000
#define DRAIN_MS   5000        /* скільки чекаємо на тих, хто вже в польоті */

static int wake[2] = { -1, -1 };          /* [0] — читати, [1] — писати з обробника */

static void on_signal(int signo)
{
    int saved = errno;                             /* чужий errno — під захист */
    unsigned char b = (unsigned char) signo;

    (void) write(wake[1], &b, 1);                  /* єдина дія обробника */
    errno = saved;
}

static int make_listener(void)
{
    struct sockaddr_in a;
    int fd, on = 1;

    fd = socket(AF_INET, SOCK_STREAM | SOCK_NONBLOCK | SOCK_CLOEXEC, 0);
    if (fd < 0)
        return -1;
    setsockopt(fd, SOL_SOCKET, SO_REUSEADDR, &on, sizeof on);

    memset(&a, 0, sizeof a);
    a.sin_family = AF_INET;
    a.sin_addr.s_addr = htonl(INADDR_ANY);
    a.sin_port = htons(PORT);

    if (bind(fd, (struct sockaddr *) &a, sizeof a) < 0 || listen(fd, 64) < 0) {
        close(fd);
        return -1;
    }
    return fd;
}

/* Обслужити готове з'єднання: 1 — живе далі, 0 — час закривати. */
static int serve(int fd)
{
    char buf[4096];
    ssize_t r, off, w = 0;

    r = read(fd, buf, sizeof buf);
    if (r == 0)
        return 0;                                  /* клієнт закрив свій кінець */
    if (r < 0)
        return errno == EAGAIN || errno == EINTR;

    for (off = 0; off < r; off += w) {             /* спрощення: черги на запис нема, */
        w = write(fd, buf + off, (size_t) (r - off));   /* справжній сервер чекав би POLLOUT */
        if (w <= 0)
            return 0;
    }
    return 1;
}

static int compact(int *v, int n)                  /* прибрати дірки після закриттів */
{
    int i, k = 0;

    for (i = 0; i < n; i++)
        if (v[i] >= 0)
            v[k++] = v[i];
    return k;
}

/* Померти саме від сигналу, а не «успішно вийти». */
static void die_by(int signo)
{
    struct sigaction dfl;
    sigset_t only;

    memset(&dfl, 0, sizeof dfl);
    dfl.sa_handler = SIG_DFL;
    sigemptyset(&dfl.sa_mask);
    sigaction(signo, &dfl, NULL);

    sigemptyset(&only);
    sigaddset(&only, signo);
    sigprocmask(SIG_UNBLOCK, &only, NULL);         /* якщо був заблокований */

    raise(signo);
    _exit(128 + signo);                            /* сюди керування не дійде */
}

int main(void)
{
    struct pollfd pfd[2 + MAX_CONN];
    struct sigaction sa;
    int conn[MAX_CONN], nconn = 0;
    int listen_fd, stopping = 0, sig_got = SIGTERM;

    if (pipe2(wake, O_NONBLOCK | O_CLOEXEC) < 0)   /* обидва прапорці обов'язкові */
        return 1;

    memset(&sa, 0, sizeof sa);
    sa.sa_handler = on_signal;
    sigemptyset(&sa.sa_mask);
    sa.sa_flags = SA_RESTART;                      /* решту викликів ядро перезапустить */
    sigaction(SIGTERM, &sa, NULL);
    sigaction(SIGINT, &sa, NULL);

    sa.sa_handler = SIG_IGN;                       /* запис у мертвий сокет — не смерть */
    sa.sa_flags = 0;
    sigaction(SIGPIPE, &sa, NULL);

    listen_fd = make_listener();
    if (listen_fd < 0)
        return 1;

    while (!stopping || nconn > 0) {
        int n, i;

        pfd[0].fd = listen_fd;             /* після close тут -1 → poll ігнорує запис */
        pfd[0].events = POLLIN;
        pfd[1].fd = wake[0];
        pfd[1].events = POLLIN;
        for (i = 0; i < nconn; i++) {
            pfd[2 + i].fd = conn[i];
            pfd[2 + i].events = POLLIN;
        }

        n = poll(pfd, (nfds_t) (2 + nconn), stopping ? DRAIN_MS : -1);
        if (n == 0)
            break;                         /* дедлайн вичерпано — доб'ємо решту */
        if (n < 0) {
            if (errno == EINTR)            /* poll не перезапускається ніколи */
                continue;
            break;
        }

        if (pfd[1].revents & POLLIN) {     /* прокинулися через сигнал */
            unsigned char b[32];
            ssize_t r;

            while ((r = read(wake[0], b, sizeof b)) > 0)
                sig_got = b[r - 1];        /* читати до EAGAIN, а не рівно один байт */

            if (!stopping) {
                stopping = 1;
                close(listen_fd);          /* порт вільний одразу */
                listen_fd = -1;
            }
        }

        if (listen_fd >= 0 && (pfd[0].revents & POLLIN)) {
            int c = accept4(listen_fd, NULL, NULL, SOCK_NONBLOCK | SOCK_CLOEXEC);

            if (c >= 0) {
                if (nconn < MAX_CONN)
                    conn[nconn++] = c;
                else
                    close(c);
            }
        }

        for (i = 0; i < nconn; i++)
            if (pfd[2 + i].revents && !serve(conn[i])) {
                close(conn[i]);
                conn[i] = -1;              /* позначити на виліт, а не двигати масив */
            }
        nconn = compact(conn, nconn);
    }

    while (nconn > 0)
        close(conn[--nconn]);
    if (listen_fd >= 0)
        close(listen_fd);
    die_by(sig_got);
    return 0;
}
