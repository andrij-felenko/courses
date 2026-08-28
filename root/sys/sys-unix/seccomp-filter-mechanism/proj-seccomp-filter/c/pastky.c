#include <signal.h>
#include <stdio.h>
#include <unistd.h>

static void on_sigsys(int sig, siginfo_t *si, void *uc)
{
    (void)sig; (void)uc;
    char buf[160];
    int n = snprintf(buf, sizeof buf,
                     "seccomp: заборонено виклик %d (arch 0x%x) з адреси %p\n",
                     si->si_syscall, si->si_arch, si->si_call_addr);
    write(STDERR_FILENO, buf, n > 0 ? (size_t)n : 0);
    _exit(159);
}

static void catch_sigsys(void)
{
    struct sigaction sa = { 0 };
    sa.sa_sigaction = on_sigsys;
    sa.sa_flags = SA_SIGINFO;
    sigemptyset(&sa.sa_mask);
    sigaction(SIGSYS, &sa, NULL);
}
