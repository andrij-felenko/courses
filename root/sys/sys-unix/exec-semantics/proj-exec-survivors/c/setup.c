/* setup.c — виставляє все, що можна виставити, і передає естафету.
   Збірка: cc -O2 -Wall -Wextra -o setup setup.c
   Запуск: ./setup ./report                                          */
#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <limits.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <sys/resource.h>
#include <sys/stat.h>
#include <sys/syscall.h>
#include <sys/time.h>
#include <time.h>
#include <unistd.h>

static void farewell(void)        /* адреса цієї функції — у старому образі */
{
    fprintf(stderr, "[стенд] atexit пережив заміну — такого не буває\n");
}

static void on_usr1(int signo) { (void) signo; }

static double cpu_now(void)
{
    struct timespec t;
    clock_gettime(CLOCK_PROCESS_CPUTIME_ID, &t);
    return t.tv_sec + t.tv_nsec / 1e9;
}

static void burn(double seconds)  /* намолоти трохи процесорного часу */
{
    volatile unsigned long long acc = 0;
    double t0 = cpu_now();
    while (cpu_now() - t0 < seconds)
        for (int i = 0; i < 200000; i++)
            acc += i;
}

int main(int argc, char **argv)
{
    char rpath[PATH_MAX];
    struct sigaction sa;
    struct sigevent sev;
    struct itimerspec its;
    struct rlimit rl;
    sigset_t block;
    void *page;
    int keep, gone, ktimer = -1;
    char e_fd[64], e_cloexec[64], e_timer[64], e_addr[64],
         e_pid[64], e_cpu[64], e_nofile[64];
    char *envp[8];

    if (argc < 2) {
        fprintf(stderr, "як користуватися: %s ПРОГРАМА [аргументи]\n", argv[0]);
        return 2;
    }
    /* шлях резолвимо ДО chdir: після нього «./report» означатиме вже інше */
    if (realpath(argv[1], rpath) == NULL) { perror(argv[1]); return 2; }

    atexit(farewell);

    /* 1. Два дескриптори на той самий файл, з різними прапорцями */
    keep = open("/tmp/exec-probe.dat", O_RDWR | O_CREAT | O_TRUNC, 0644);
    if (keep < 0) { perror("open"); return 1; }
    if (write(keep, "0123456789abcdefghijklmnopqrstuv", 32) != 32) {
        perror("write"); return 1;
    }
    lseek(keep, 10, SEEK_SET);            /* зсув, який має пережити заміну */
    gone = open("/tmp/exec-probe.dat", O_RDONLY | O_CLOEXEC);
    if (gone < 0) { perror("open O_CLOEXEC"); return 1; }

    /* 2. Прості властивості процесу */
    umask(0027);
    if (chdir("/tmp") != 0) { perror("chdir"); return 1; }
    getrlimit(RLIMIT_NOFILE, &rl);
    if (rl.rlim_cur > 512) { rl.rlim_cur = 512; setrlimit(RLIMIT_NOFILE, &rl); }
    if (setpriority(PRIO_PROCESS, 0, 5) != 0)
        fprintf(stderr, "[стенд] nice не виставився (%s) — звіт це покаже\n",
                strerror(errno));

    /* 3. Сигнали: обробник, ігнорування, маска, відкладений */
    memset(&sa, 0, sizeof sa);
    sigemptyset(&sa.sa_mask);
    sa.sa_handler = on_usr1;
    sigaction(SIGUSR1, &sa, NULL);        /* спіймано → буде скинуто */
    sa.sa_handler = SIG_IGN;
    sigaction(SIGTERM, &sa, NULL);        /* ігнорування → лишиться */

    sigemptyset(&block);
    sigaddset(&block, SIGUSR2);
    sigprocmask(SIG_BLOCK, &block, NULL); /* СПЕРШУ маска... */
    kill(getpid(), SIGUSR2);              /* ...а тоді сигнал самому собі */

    /* 4. Дві породи таймерів */
    alarm(300);                           /* інтервальний, він же ITIMER_REAL */

    memset(&sev, 0, sizeof sev);
    sev.sigev_notify = SIGEV_SIGNAL;
    sev.sigev_signo  = SIGUSR2;
    if (syscall(SYS_timer_create, CLOCK_MONOTONIC, &sev, &ktimer) != 0) {
        perror("timer_create"); return 1;
    }
    memset(&its, 0, sizeof its);
    its.it_value.tv_sec = 600;
    if (syscall(SYS_timer_settime, ktimer, 0, &its, NULL) != 0) {
        perror("timer_settime"); return 1;
    }

    /* 5. Сторінка пам'яті — те, на що можна послатися лише адресою */
    page = mmap(NULL, 4096, PROT_READ | PROT_WRITE,
                MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    if (page == MAP_FAILED) { perror("mmap"); return 1; }
    strcpy((char *) page, "я жив у старому образі");

    burn(0.15);

    /* 6. Єдиний багаж, що переїде: рядки оточення */
    snprintf(e_fd,      sizeof e_fd,      "SURV_FD=%d", keep);
    snprintf(e_cloexec, sizeof e_cloexec, "SURV_FD_CLOEXEC=%d", gone);
    snprintf(e_timer,   sizeof e_timer,   "SURV_TIMER=%d", ktimer);
    snprintf(e_addr,    sizeof e_addr,    "SURV_ADDR=%p", page);
    snprintf(e_pid,     sizeof e_pid,     "SURV_PID=%ld", (long) getpid());
    snprintf(e_cpu,     sizeof e_cpu,     "SURV_CPU=%.3f", cpu_now());
    snprintf(e_nofile,  sizeof e_nofile,  "SURV_NOFILE=%llu",
             (unsigned long long) rl.rlim_cur);
    envp[0] = e_fd;  envp[1] = e_cloexec; envp[2] = e_timer;  envp[3] = e_addr;
    envp[4] = e_pid; envp[5] = e_cpu;     envp[6] = e_nofile; envp[7] = NULL;

    printf("[стенд] pid %ld: fd %d без CLOEXEC (зсув 10), fd %d з O_CLOEXEC,\n"
           "        SIGUSR2 заблоковано й надіслано собі, alarm(300),\n"
           "        POSIX-таймер #%d, сторінка на %p, намелено %.3f с\n\n",
           (long) getpid(), keep, gone, ktimer, page, cpu_now());

    fflush(NULL);        /* буфери stdio — теж пам'ять старого образу */
    execve(rpath, &argv[1], envp);
    perror("execve");
    _exit(127);
}
