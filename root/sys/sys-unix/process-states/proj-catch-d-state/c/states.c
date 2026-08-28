/* states.c — піддослідний: сам себе проводити крізь R, S, T, Z і D.
 * Збірка:  cc -O2 -o states states.c
 * Запуск:  ./states &   (у фоні, бо фаза T зупиняє процес)
 */
#define _GNU_SOURCE
#include <sched.h>
#include <signal.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
#include <sys/wait.h>
#include <time.h>
#include <unistd.h>

static double now(void)
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec + ts.tv_nsec * 1e-9;
}

static double t0;

static void banner(const char *tag, const char *why)
{
    fprintf(stderr, "%7.3f  [%s] %s\n", now() - t0, tag, why);
    fflush(stderr);
}

/* Літера стану з /proc/PID/stat.
   Друге поле — ім'я програми в дужках, і воно може містити і пробіли,
   і самі дужки. Тому єдиний надійний спосіб — шукати ОСТАННЮ ')'. */
static char state_of(pid_t pid)
{
    char path[64], buf[512];
    snprintf(path, sizeof path, "/proc/%d/stat", (int)pid);
    FILE *f = fopen(path, "r");
    if (!f) return '?';
    size_t n = fread(buf, 1, sizeof buf - 1, f);
    fclose(f);
    buf[n] = '\0';
    char *p = strrchr(buf, ')');
    return (p && p[1] && p[2]) ? p[2] : '?';
}

/* ── R: нічого не бракує, крім вільного ядра ────────────────────────── */
static void phase_running(double secs)
{
    banner("R", "порожній цикл: задача стоїть у черзі готових");
    double end = now() + secs;
    volatile unsigned long x = 0;
    while (now() < end)
        for (int i = 0; i < 100000; i++) x++;
}

/* ── S: сон, який будить і таймер, і сигнал ─────────────────────────── */
static void phase_sleeping(int secs)
{
    banner("S", "nanosleep: переривний сон");
    struct timespec ts = { secs, 0 };
    nanosleep(&ts, NULL);
}

/* ── T: задача не чекає нічого, їй заборонено бігти ─────────────────── */
static void phase_stopped(void)
{
    banner("T", "raise(SIGSTOP): вийти можна лише через SIGCONT");
    raise(SIGSTOP);
    banner("T", "прийшов SIGCONT — знову в черзі готових");
}

/* ── Z: зомбі. Це окремий PID — наша дитина, не ми ──────────────────── */
static void phase_zombie(int secs)
{
    pid_t kid = fork();
    if (kid == 0) _exit(42);

    struct timespec ts = { 0, 50 * 1000 * 1000 };
    nanosleep(&ts, NULL);                  /* дати дитині вийти */
    fprintf(stderr, "%7.3f  [Z] дитина %d у стані '%c' — код виходу ще нічий\n",
            now() - t0, (int)kid, state_of(kid));

    ts.tv_sec = secs; ts.tv_nsec = 0;
    nanosleep(&ts, NULL);
    waitpid(kid, NULL, 0);
    banner("Z", "wait() забрав код виходу — запис зник");
}

/* ── D: непереривний сон на замовлення ──────────────────────────────── */
#define STACK_SZ (256 * 1024)
static int hold_seconds;

static int vfork_child(void *arg)
{
    struct timespec ts = { *(int *)arg, 0 };
    nanosleep(&ts, NULL);
    _exit(0);
}

static void phase_disk_sleep(int secs)
{
    void *stack = mmap(NULL, STACK_SZ, PROT_READ | PROT_WRITE,
                       MAP_PRIVATE | MAP_ANONYMOUS | MAP_STACK, -1, 0);
    if (stack == MAP_FAILED) { perror("mmap"); return; }

    hold_seconds = secs;
    banner("D", "clone(CLONE_VFORK): батько стоїть, поки дитина не вийде");
    fprintf(stderr, "         спробуйте в іншому терміналі:  kill -TERM %d\n"
                    "         обробника на TERM нема, тож цей D від нього гине\n",
            (int)getpid());
    fflush(stderr);

    pid_t kid = clone(vfork_child, (char *)stack + STACK_SZ,
                      CLONE_VFORK | SIGCHLD, &hold_seconds);
    if (kid < 0) { perror("clone"); return; }

    waitpid(kid, NULL, 0);
    munmap(stack, STACK_SZ);
    banner("D", "дитина вийшла — батько прокинувся");
}

int main(void)
{
    t0 = now();
    setvbuf(stderr, NULL, _IONBF, 0);
    fprintf(stderr, "PID %d\n", (int)getpid());

    phase_running(3.0);
    phase_sleeping(3);
    phase_stopped();
    phase_zombie(3);
    phase_disk_sleep(12);
    return 0;
}
