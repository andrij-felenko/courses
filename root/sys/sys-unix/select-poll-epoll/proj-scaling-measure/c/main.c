#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <errno.h>
#include <time.h>
#include <sched.h>
#include <poll.h>
#include <sys/select.h>
#include <sys/epoll.h>
#include <sys/resource.h>
#include <sys/socket.h>

enum { SELECT, POLL, EPOLL };

static int *rfd, *wfd;              /* кінці пар: за яким чекаємо / у який штовхаємо */
static struct pollfd *pfds;
static int epfd = -1, maxfd = 0;

static long long now_ns(void) {     /* монотонний годинник: не стрибає від NTP */
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (long long)ts.tv_sec * 1000000000LL + ts.tv_nsec;
}

static void raise_nofile(rlim_t want) {
    struct rlimit rl;
    if (getrlimit(RLIMIT_NOFILE, &rl) != 0) { perror("getrlimit"); exit(1); }
    if (rl.rlim_cur >= want) return;
    if (want > rl.rlim_max) {
        fprintf(stderr, "тверда межа %llu < потрібних %llu — підніміть fs.nr_open\n",
                (unsigned long long)rl.rlim_max, (unsigned long long)want);
        want = rl.rlim_max;         /* беремо все, що дозволено без привілеїв */
    }
    rl.rlim_cur = want;
    if (setrlimit(RLIMIT_NOFILE, &rl) != 0) { perror("setrlimit"); exit(1); }
}

static void make_pairs(int n) {
    rfd  = malloc(n * sizeof *rfd);
    wfd  = malloc(n * sizeof *wfd);
    pfds = malloc(n * sizeof *pfds);
    epfd = epoll_create1(0);
    maxfd = epfd;
    for (int i = 0; i < n; i++) {
        int sv[2];
        /* SOCK_NONBLOCK одразу в socketpair: без O_NONBLOCK дослід зависне */
        if (socketpair(AF_UNIX, SOCK_STREAM | SOCK_NONBLOCK, 0, sv) != 0) {
            perror("socketpair");   /* найчастіше EMFILE: не підняли межу */
            exit(1);
        }
        rfd[i] = sv[0];  wfd[i] = sv[1];
        if (sv[0] > maxfd) maxfd = sv[0];
        if (sv[1] > maxfd) maxfd = sv[1];
        pfds[i].fd = sv[0];  pfds[i].events = POLLIN;
        struct epoll_event ev = { .events = EPOLLIN, .data = { .u32 = i } };
        epoll_ctl(epfd, EPOLL_CTL_ADD, sv[0], &ev);
    }
}

static long long bench(int method, int n, int iters) {
    fd_set master, ready;
    struct epoll_event out[8];
    long long total = 0;
    char b;

    if (method == SELECT) {         /* маску будуємо раз, копіюємо щоразу */
        FD_ZERO(&master);
        for (int i = 0; i < n; i++) FD_SET(rfd[i], &master);
    }

    for (int k = 0; k < iters; k++) {
        int hot = k % n;            /* активний по черзі, а не той самий */
        if (write(wfd[hot], "x", 1) != 1) { perror("write"); exit(1); }

        long long t0 = now_ns();
        int got;
        switch (method) {
        case SELECT:
            ready = master;         /* ядро псує маску на місці — копія обов'язкова */
            got = select(maxfd + 1, &ready, NULL, NULL, NULL);
            break;
        case POLL:
            got = poll(pfds, n, -1);        /* revents ядро перезаписує саме */
            break;
        default:
            got = epoll_wait(epfd, out, 8, -1);
        }
        long long t1 = now_ns();
        if (got != 1) { fprintf(stderr, "чекали рівно одну подію, дістали %d\n", got); exit(1); }
        total += t1 - t0;

        while (read(rfd[hot], &b, 1) > 0) { }   /* до EAGAIN, інакше подія лишиться */
    }
    return total / iters;
}

static int cmp_ll(const void *a, const void *b) {
    long long x = *(const long long *)a, y = *(const long long *)b;
    return (x > y) - (x < y);
}

static long long median(int method, int n, int iters, int runs) {
    long long r[9];
    if (runs > 9) runs = 9;
    for (int i = 0; i < runs; i++) r[i] = bench(method, n, iters);
    qsort(r, runs, sizeof r[0], cmp_ll);
    return r[runs / 2];
}

int main(void) {
    static const int sizes[] = { 100, 500, 1000, 10000, 100000 };
    cpu_set_t cpus;

    raise_nofile(2 * 100000 + 64);          /* дві половини пари плюс запас */
    CPU_ZERO(&cpus);  CPU_SET(0, &cpus);
    sched_setaffinity(0, sizeof cpus, &cpus);   /* без міграцій між ядрами */

    printf("      N    select      poll     epoll   (мкс на одне очікування)\n");
    for (size_t s = 0; s < sizeof sizes / sizeof *sizes; s++) {
        int n = sizes[s], iters = n > 10000 ? 2000 : 20000;
        char sel[16];

        make_pairs(n);
        bench(POLL, n, 1000);               /* прогрів: сторінки, кеші, частота */

        if (maxfd < FD_SETSIZE)
            snprintf(sel, sizeof sel, "%.2f", median(SELECT, n, iters, 7) / 1000.0);
        else
            snprintf(sel, sizeof sel, "%s", "--");

        printf("%7d  %8s  %8.2f  %8.2f\n", n, sel,
               median(POLL,  n, iters, 7) / 1000.0,
               median(EPOLL, n, iters, 7) / 1000.0);
        fflush(stdout);

        for (int i = 0; i < n; i++) { close(rfd[i]); close(wfd[i]); }
        close(epfd);  free(rfd);  free(wfd);  free(pfds);
    }
    return 0;
}
