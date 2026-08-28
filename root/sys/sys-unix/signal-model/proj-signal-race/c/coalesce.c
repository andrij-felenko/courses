/* coalesce.c — скільки з N надісланих сигналів справді доправлено.
 * gcc -O2 -Wall -o coalesce coalesce.c      запуск: ./coalesce 1000
 */
#define _POSIX_C_SOURCE 199309L
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>

#define OK(call) do { if ((call) != 0) { perror(#call); return 1; } } while (0)
#define MAXLOG 4096

static volatile sig_atomic_t plain_hits = 0;   /* запусків обробника SIGUSR1     */
static volatile sig_atomic_t rt_hits    = 0;   /* запусків обробника SIGRTMIN+1  */
static volatile sig_atomic_t rt_log[MAXLOG];   /* значення в порядку надходження */

static void on_plain(int sig)
{
    (void) sig;
    plain_hits++;                    /* нічого більше: обробник — не місце для printf */
}

static void on_rt(int sig, siginfo_t *si, void *ctx)
{
    (void) sig; (void) ctx;
    int i = rt_hits;                 /* сам себе цей обробник не перериває:       */
    if (i < MAXLOG)                  /* на час його роботи ядро блокує його сигнал */
        rt_log[i] = si->si_value.sival_int;
    rt_hits = i + 1;
}

int main(int argc, char **argv)
{
    int n = (argc > 1) ? atoi(argv[1]) : 1000;
    const int RT = SIGRTMIN + 1;     /* SIGRTMIN — виклик функції, не стала */
    struct sigaction sa;
    sigset_t block, old, pend;

    memset(&sa, 0, sizeof sa);
    sa.sa_handler = on_plain;
    sigemptyset(&sa.sa_mask);
    OK(sigaction(SIGUSR1, &sa, NULL));

    memset(&sa, 0, sizeof sa);
    sa.sa_sigaction = on_rt;
    sa.sa_flags = SA_SIGINFO;        /* без цього обробник не побачить si_value */
    sigemptyset(&sa.sa_mask);
    OK(sigaction(RT, &sa, NULL));

    sigemptyset(&block);
    sigaddset(&block, SIGUSR1);
    sigaddset(&block, RT);
    OK(sigprocmask(SIG_BLOCK, &block, &old));   /* ворота зачинено */

    for (int i = 1; i <= n; i++)
        raise(SIGUSR1);

    int queued = 0;
    for (int i = 1; i <= n; i++) {
        union sigval v = { .sival_int = i };    /* вантаж: порядковий номер */
        if (sigqueue(getpid(), RT, v) == 0) { queued++; continue; }
        if (errno == EAGAIN) {
            printf("черга сповнилася на %d-му записі (EAGAIN)\n", i);
            break;
        }
        perror("sigqueue");
        return 1;
    }

    OK(sigpending(&pend));                      /* що ядро тримає просто зараз */
    printf("до розблокування: біт SIGUSR1=%d, біт SIGRTMIN+1=%d\n",
           sigismember(&pend, SIGUSR1), sigismember(&pend, RT));

    OK(sigprocmask(SIG_SETMASK, &old, NULL));   /* тут усе й доправиться */

    printf("SIGUSR1:     надіслано %d, доправлено %d\n", n, (int) plain_hits);
    printf("SIGRTMIN+1:  у черзі %d, доправлено %d\n", queued, (int) rt_hits);

    int ordered = 1;
    for (int i = 0; i < (int) rt_hits && i < MAXLOG; i++)
        if (rt_log[i] != i + 1) { ordered = 0; break; }
    printf("порядок значень: %s\n", ordered ? "рівно 1,2,3,…" : "порушено");
    return 0;
}
