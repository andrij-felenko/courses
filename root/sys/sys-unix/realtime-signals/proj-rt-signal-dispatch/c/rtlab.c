/* rtlab.c — дослід над реальночасовими сигналами: порядок, бюджет, ціна. */
#define _POSIX_C_SOURCE 200809L
#include <errno.h>
#include <signal.h>
#include <stdio.h>
#include <string.h>
#include <time.h>
#include <unistd.h>
#include <sys/resource.h>
#include <sys/wait.h>

#define SIG_STOP (SIGRTMIN + 0)   /* менший номер — має обганяти */
#define SIG_JOB  (SIGRTMIN + 1)   /* потік завдань */
#define REPS     200000

static sigset_t rtset(void)
{
    sigset_t s;
    sigemptyset(&s);
    sigaddset(&s, SIG_STOP);
    sigaddset(&s, SIG_JOB);
    return s;
}

static long long now_ns(void)
{
    struct timespec t;
    clock_gettime(CLOCK_MONOTONIC, &t);
    return t.tv_sec * 1000000000LL + t.tv_nsec;
}

/* ── 1. Чи справді менший номер обганяє більший ─────────────────────────── */
static void exp_order(void)
{
    int barrier[2];
    if (pipe(barrier) == -1) { perror("pipe"); return; }

    sigset_t s = rtset();
    sigprocmask(SIG_BLOCK, &s, NULL);   /* ДО fork: дитина успадкує маску */
    fflush(stdout);                     /* щоб буфер не роздвоївся */

    pid_t child = fork();
    if (child == 0) {
        char go;
        close(barrier[1]);
        if (read(barrier[0], &go, 1) != 1) _exit(1);   /* чекаємо: чергу наповнено */

        int first = -1, first_val = 0, n_job = 0, out_of_order = 0;
        for (;;) {
            siginfo_t si;
            struct timespec tmo = { .tv_sec = 1, .tv_nsec = 0 };
            int sig = sigtimedwait(&s, &si, &tmo);
            if (sig == -1) {
                if (errno == EINTR) continue;          /* урвав сигнал поза набором */
                break;                                 /* EAGAIN: черга порожня */
            }
            if (first == -1) { first = sig; first_val = si.si_value.sival_int; }
            if (sig == SIG_JOB && si.si_value.sival_int != n_job++) out_of_order++;
        }
        printf("  перший забраний: SIGRTMIN+%d, вантаж %d\n",
               first - SIGRTMIN, first_val);
        printf("  записів SIGRTMIN+1 забрано: %d, збоїв порядку: %d\n",
               n_job, out_of_order);
        fflush(stdout);
        _exit(0);
    }

    close(barrier[0]);
    union sigval v;
    for (int i = 0; i < 100; i++) {          /* спершу сто — у БІЛЬШИЙ номер */
        v.sival_int = i;
        if (sigqueue(child, SIG_JOB, v) == -1) { perror("sigqueue"); break; }
    }
    v.sival_int = 999;                       /* аж потім один — у МЕНШИЙ */
    sigqueue(child, SIG_STOP, v);

    if (write(barrier[1], "g", 1) != 1) perror("write");
    close(barrier[1]);
    wait(NULL);
}

/* ── 2. Скільки записів дозволять покласти ──────────────────────────────── */
static void exp_budget(void)
{
    struct rlimit rl;
    getrlimit(RLIMIT_SIGPENDING, &rl);
    printf("  RLIMIT_SIGPENDING: %lu\n", (unsigned long)rl.rlim_cur);

    sigset_t s = rtset();
    sigprocmask(SIG_BLOCK, &s, NULL);   /* інакше перший же запис нас уб'є */

    union sigval v;
    long n = 0;
    for (;;) {
        v.sival_int = (int)n;
        if (sigqueue(getpid(), SIG_JOB, v) == -1) {
            printf("  покладено %ld, далі — %s\n", n, strerror(errno));
            break;
        }
        n++;
    }

    FILE *f = fopen("/proc/self/status", "r");
    char line[256];
    while (f && fgets(line, sizeof line, f))
        if (strncmp(line, "SigQ:", 5) == 0) printf("  %s", line);
    if (f) fclose(f);

    siginfo_t si;                       /* повернути квоту решті процесів */
    struct timespec zero = { 0, 0 };
    while (sigtimedwait(&s, &si, &zero) > 0) { }
}

/* ── 3. Скільки коштує подія проти байта в каналі ───────────────────────── */
static void exp_cost(void)
{
    sigset_t s = rtset();
    sigprocmask(SIG_BLOCK, &s, NULL);

    pid_t me = getpid();
    union sigval v;
    siginfo_t si;
    struct timespec zero = { 0, 0 };

    long long t0 = now_ns();
    for (int i = 0; i < REPS; i++) {
        v.sival_int = i;
        if (sigqueue(me, SIG_JOB, v) == -1)      { perror("sigqueue");    return; }
        if (sigtimedwait(&s, &si, &zero) == -1)  { perror("sigtimedwait"); return; }
    }
    long long t_sig = now_ns() - t0;

    int p[2], job;
    if (pipe(p) == -1) { perror("pipe"); return; }
    t0 = now_ns();
    for (int i = 0; i < REPS; i++) {
        job = i;
        if (write(p[1], &job, sizeof job) != (ssize_t)sizeof job) return;
        if (read(p[0], &job, sizeof job) != (ssize_t)sizeof job) return;
    }
    long long t_pipe = now_ns() - t0;

    printf("  sigqueue + sigtimedwait: %lld нс на подію\n", t_sig / REPS);
    printf("  write + read у канал:    %lld нс на подію\n", t_pipe / REPS);
}

int main(int argc, char **argv)
{
    const char *what = argc > 1 ? argv[1] : "order";
    printf("SIGRTMIN=%d SIGRTMAX=%d\n", SIGRTMIN, SIGRTMAX);

    if      (!strcmp(what, "order"))  exp_order();
    else if (!strcmp(what, "budget")) exp_budget();
    else if (!strcmp(what, "cost"))   exp_cost();
    else { fprintf(stderr, "вживання: %s order|budget|cost\n", argv[0]); return 2; }
    return 0;
}
