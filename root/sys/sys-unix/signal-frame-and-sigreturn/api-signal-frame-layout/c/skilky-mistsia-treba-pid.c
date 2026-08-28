#define _GNU_SOURCE
#include <signal.h>
#include <unistd.h>
#include <stdlib.h>

static void install_altstack(void)
{
    size_t   sz = (size_t)sysconf(_SC_SIGSTKSZ);
    stack_t  ss = { .ss_sp = malloc(sz), .ss_flags = 0, .ss_size = sz };
    sigaltstack(&ss, NULL);

    struct sigaction sa = { 0 };
    sa.sa_sigaction = on_segv;
    sa.sa_flags     = SA_SIGINFO | SA_ONSTACK;
    sigemptyset(&sa.sa_mask);
    sigaction(SIGSEGV, &sa, NULL);
}
