#define _GNU_SOURCE
#include <signal.h>
#include <ucontext.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/mman.h>

/* Мітки всередині ризикованої дільниці: асемблер робить із них звичайні
   символи, тож обробник знає точні адреси — і де дозволено впасти,
   і обидва місця, куди можна приземлитися. */
extern const char probe_fault[], probe_after[], probe_fail[];

enum { MODE_BAIL, MODE_SKIP };
static volatile sig_atomic_t mode = MODE_BAIL;
static void * volatile last_fault;        /* si_addr останнього перехоплення */

static void on_segv(int sig, siginfo_t *si, void *ctx)
{
    ucontext_t *uc = ctx;
    greg_t *r = uc->uc_mcontext.gregs;    /* НЕ копія — сам кадр на стеку */

    /* Єдина інструкція, збій на якій ми вміємо лагодити. Усе інше —
       справжня помилка: знімаємо обробник і даємо процесові чесно
       померти на тому самому місці. */
    if ((const char *)(uintptr_t)r[REG_RIP] != probe_fault) {
        signal(sig, SIG_DFL);
        return;
    }

    last_fault = si->si_addr;             /* адреса, до якої не вийшло дійти */

    if (mode == MODE_BAIL) {
        r[REG_RIP] = (greg_t)(uintptr_t)probe_fail;   /* вихід із дільниці */
    } else {
        r[REG_RAX] = 0;                               /* значення-заглушка */
        r[REG_RIP] = (greg_t)(uintptr_t)probe_after;  /* пропуск інструкції */
    }
}

/* noinline + noclone: вставка з глобальними мітками мусить потрапити
   в об'єктний файл РІВНО один раз, інакше буде подвійне визначення. */
__attribute__((noinline, noclone))
static int try_read64(const void *p, uint64_t *out)
{
    uint64_t v;
    int ok;
    __asm__ volatile(
        ".globl probe_fault, probe_after, probe_fail\n"
        "probe_fault: movq (%[p]), %%rax\n"
        "probe_after: movl $1, %[ok]\n"
        "             jmp  1f\n"
        "probe_fail:  movl $0, %[ok]\n"
        "1:\n"
        : "=a"(v), [ok] "=&r"(ok)
        : [p] "r"(p)
        : "cc", "memory");
    if (ok)
        *out = v;
    return ok;
}

static void install_handler(void)
{
    /* Розмір площадки — лише через sysconf: у glibc від 2.34 SIGSTKSZ
       уже не стала часу компіляції. */
    long sz = sysconf(_SC_SIGSTKSZ);
    if (sz <= 0)
        sz = 32 * 1024;

    stack_t ss;
    ss.ss_sp = malloc((size_t)sz);
    ss.ss_size = (size_t)sz;
    ss.ss_flags = 0;
    if (!ss.ss_sp || sigaltstack(&ss, NULL) != 0) {
        perror("sigaltstack");
        exit(1);
    }

    struct sigaction sa;
    memset(&sa, 0, sizeof sa);
    sa.sa_sigaction = on_segv;
    sa.sa_flags = SA_SIGINFO | SA_ONSTACK;   /* розширений обробник, на площадці */
    sigfillset(&sa.sa_mask);
    if (sigaction(SIGSEGV, &sa, NULL) != 0) {
        perror("sigaction");
        exit(1);
    }
}

int main(void)
{
    install_handler();

    uint64_t good = 0x1122334455667788ULL, v = 0xdead;
    char *closed = mmap(NULL, 4096, PROT_NONE,
                        MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    if (closed == MAP_FAILED)
        return 1;

    int ok = try_read64(&good, &v);
    printf("добра адреса      : ok=%d v=0x%llx\n", ok, (unsigned long long)v);

    mode = MODE_BAIL;
    ok = try_read64(closed, &v);
    printf("закрита, «вихід»  : ok=%d v=0x%llx si_addr=%p\n",
           ok, (unsigned long long)v, last_fault);

    mode = MODE_SKIP;
    ok = try_read64(closed, &v);
    printf("закрита, «пропуск»: ok=%d v=0x%llx si_addr=%p\n",
           ok, (unsigned long long)v, last_fault);

    puts("програма жива");
    return 0;
}
