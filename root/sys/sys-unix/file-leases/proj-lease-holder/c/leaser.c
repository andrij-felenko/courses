/* leaser.c — тримає оренду на запис і встигає відповісти вчасно.
 * gcc -O2 -Wall -o leaser leaser.c
 * ./leaser /tmp/leased.dat [--silent] [--work=МС]                    */
#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <poll.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>

static int wake[2];        /* самотруба: [0] читає цикл, [1] пише обробник */

static void on_break(int sig, siginfo_t *si, void *uc)
{
    (void)sig; (void)uc;
    int saved = errno;                      /* write поставить свій errno   */
    unsigned char fd = (unsigned char)si->si_fd;
    ssize_t n = write(wake[1], &fd, 1);     /* єдина дозволена тут дія      */
    (void)n;
    errno = saved;
}

static double now_ms(void)
{
    struct timespec t;
    clock_gettime(CLOCK_MONOTONIC, &t);
    return t.tv_sec * 1e3 + t.tv_nsec / 1e6;
}

int main(int argc, char **argv)
{
    const char *path = (argc > 1) ? argv[1] : "/tmp/leased.dat";
    int silent = 0, work_ms = 0;
    for (int i = 2; i < argc; i++) {
        if (!strcmp(argv[i], "--silent"))        silent = 1;
        else if (!strncmp(argv[i], "--work=", 7)) work_ms = atoi(argv[i] + 7);
    }

    /* O_RDONLY — не недогляд, а умова майбутнього зниження (див. нижче). */
    int fd = open(path, O_RDONLY);
    if (fd < 0) { perror("open"); return 1; }

    if (pipe2(wake, O_CLOEXEC | O_NONBLOCK) < 0) { perror("pipe2"); return 1; }

    struct sigaction sa;
    memset(&sa, 0, sizeof sa);
    sa.sa_sigaction = on_break;
    sa.sa_flags = SA_SIGINFO | SA_RESTART;
    sigaction(SIGRTMIN, &sa, NULL);

    if (fcntl(fd, F_SETSIG, SIGRTMIN) < 0) { perror("F_SETSIG"); return 1; }
    if (fcntl(fd, F_SETOWN, getpid())  < 0) { perror("F_SETOWN"); return 1; }
    if (fcntl(fd, F_SETLEASE, F_WRLCK) < 0) {
        /* EINVAL — не звичайний файл, ФС без оренд або leases-enable = 0;
           EAGAIN — файл уже хтось тримає відкритим;
           EACCES — файл чужий, а CAP_LEASE у нас немає.                */
        perror("F_SETLEASE(F_WRLCK)");
        return 1;
    }
    printf("оренда взята на %s, чекаємо\n", path);
    fflush(stdout);

    struct pollfd pf = { .fd = wake[0], .events = POLLIN, .revents = 0 };
    for (;;) {
        if (poll(&pf, 1, -1) < 0) {
            if (errno == EINTR) continue;   /* poll не рестартується й із SA_RESTART */
            perror("poll"); return 1;
        }
        unsigned char b;
        while (read(wake[0], &b, 1) == 1) {
            double t0 = now_ms();
            if (silent) {
                printf("перерву помічено на fd=%u — навмисно мовчимо\n", b);
                fflush(stdout);
                continue;
            }
            if (work_ms) {                  /* модель «скидання кешу»      */
                struct timespec ts = { work_ms / 1000,
                                       (work_ms % 1000) * 1000000L };
                nanosleep(&ts, NULL);
            }
            /* під час перерви F_GETLEASE віддає не теперішній стан оренди,
               а ТОЙ, ЯКОГО ядро від нас чекає.                            */
            int want = fcntl(fd, F_GETLEASE);
            if (want == F_RDLCK && fcntl(fd, F_SETLEASE, F_RDLCK) == 0)
                printf("знижено до F_RDLCK за %.2f мс\n", now_ms() - t0);
            else if (fcntl(fd, F_SETLEASE, F_UNLCK) == 0)
                printf("віддано зовсім за %.2f мс\n", now_ms() - t0);
            else
                perror("F_SETLEASE");
            fflush(stdout);
        }
    }
}
