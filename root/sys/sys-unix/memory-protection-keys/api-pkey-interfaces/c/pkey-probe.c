/* pkey-probe.c — cc -O2 -o pkey-probe pkey-probe.c */
#define _GNU_SOURCE
#include <signal.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <sys/mman.h>

static void on_segv(int sig, siginfo_t *si, void *ucontext)
{
    char msg[] = "SEGV_PKUERR, si_pkey = _\n";
    (void)sig; (void)ucontext;

    if (si->si_code != SEGV_PKUERR)
        _exit(2);                       /* звичайне порушення прав ділянки */

    msg[23] = "0123456789abcdef"[si->si_pkey & 0xf];
    ssize_t n = write(STDERR_FILENO, msg, sizeof msg - 1);
    (void)n;
    _exit(0);                           /* повертатися нікуди: звернення повториться */
}

int main(void)
{
    size_t ps = (size_t)sysconf(_SC_PAGESIZE);
    char *page = mmap(NULL, ps, PROT_READ | PROT_WRITE,
                      MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    if (page == MAP_FAILED) { perror("mmap"); return 1; }
    page[0] = 'x';

    int pkey = pkey_alloc(0, PKEY_DISABLE_ACCESS);
    if (pkey < 0) { perror("pkey_alloc"); return 1; }   /* ENOSPC — ключів немає */

    if (pkey_mprotect(page, ps, PROT_READ | PROT_WRITE, pkey) < 0) {
        perror("pkey_mprotect"); return 1;
    }

    struct sigaction sa;
    memset(&sa, 0, sizeof sa);
    sa.sa_sigaction = on_segv;
    sa.sa_flags = SA_SIGINFO;
    sigemptyset(&sa.sa_mask);
    sigaction(SIGSEGV, &sa, NULL);

    printf("ключ %d, права зараз %d\n", pkey, pkey_get(pkey));

    pkey_set(pkey, 0);                            /* відчинили — лише цьому потокові */
    printf("крізь відчинений ключ читається: %c\n", page[0]);
    pkey_set(pkey, PKEY_DISABLE_ACCESS);          /* зачинили */
    fflush(stdout);

    volatile char *probe = page;
    (void)*probe;                                 /* тут спрацює ключ */

    puts("сюди виконання не доходить");
    return 0;
}
