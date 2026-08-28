/* pkey-guard.c — сторож над секретом і вимір ціни двох способів
 *   cc -O2 -pthread -o pkey-guard pkey-guard.c
 */
#define _GNU_SOURCE
#include <errno.h>
#include <pthread.h>
#include <sched.h>
#include <setjmp.h>
#include <signal.h>
#include <stdatomic.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>
#include <sys/mman.h>

static long page_size;
static sigjmp_buf escape;

/* друк з обробника: лише write(), лише власна лічба */
static void put(const char *s, size_t n) { if (write(2, s, n) < 0) _exit(2); }
#define PUT(s) put(s, sizeof(s) - 1)

static void putnum(long v)
{
    char b[24];
    int i = (int)sizeof b;
    unsigned long u = (v < 0) ? -(unsigned long)v : (unsigned long)v;
    if (!u) b[--i] = '0';
    while (u) { b[--i] = (char)('0' + u % 10); u /= 10; }
    if (v < 0) b[--i] = '-';
    put(b + i, (size_t)((int)sizeof b - i));
}

static void on_segv(int sig, siginfo_t *si, void *uc)
{
    (void)sig; (void)uc;
    if (si->si_code == SEGV_PKUERR) {
        PUT("  [обробник] заборонив КЛЮЧ: si_code = SEGV_PKUERR, si_pkey = ");
        putnum(si->si_pkey);
    } else {
        PUT("  [обробник] заборонили права ділянки: si_code = ");
        putnum(si->si_code);
    }
    PUT("\n");
    siglongjmp(escape, 1);
}

/* стек обробника — у .bss, тобто під ключем 0, і це навмисно */
static char altstack[64 * 1024];

static void install_handler(void)
{
    stack_t ss;
    struct sigaction sa;

    ss.ss_sp = altstack;
    ss.ss_size = sizeof altstack;
    ss.ss_flags = 0;
    if (sigaltstack(&ss, NULL) < 0) { perror("sigaltstack"); exit(1); }

    memset(&sa, 0, sizeof sa);
    sa.sa_sigaction = on_segv;
    sa.sa_flags = SA_SIGINFO | SA_ONSTACK;
    sigemptyset(&sa.sa_mask);
    if (sigaction(SIGSEGV, &sa, NULL) < 0) { perror("sigaction"); exit(1); }
}

static char *map_pages(size_t npages)
{
    size_t len = npages * (size_t)page_size;
    void *p = mmap(NULL, len, PROT_READ | PROT_WRITE,
                   MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    if (p == MAP_FAILED) { perror("mmap"); exit(1); }
    memset(p, 0, len);              /* заселити сторінки: без цього нічого міряти */
    return p;
}

static void demo_guard(void)
{
    char *secret = map_pages(1);
    int key;

    strcpy(secret, "приватний ключ");

    key = pkey_alloc(0, PKEY_DISABLE_ACCESS);
    if (key < 0) {
        fprintf(stderr, "pkey_alloc: %s — або ключі скінчилися, "
                        "або машина чи ядро їх не підтримують\n", strerror(errno));
        exit(1);
    }
    if (pkey_mprotect(secret, (size_t)page_size, PROT_READ | PROT_WRITE, key) < 0) {
        perror("pkey_mprotect"); exit(1);
    }
    printf("ключ %d повішено на сторінку; права ключа зараз: %d\n",
           key, pkey_get(key));

    if (sigsetjmp(escape, 1) == 0) {
        volatile char c = secret[0];        /* сюди має вдарити SIGSEGV */
        (void)c;
        printf("ЗВЕРНЕННЯ ПРОЙШЛО — ключі на цій машині не діють\n");
    } else {
        printf("повернулися з обробника: сторож на місці\n");
    }

    /* після siglongjmp ми обійшли sigreturn, тож у PKRU лишилося типове
       значення, яке ядро поставило перед обробником; ставимо своє явно */
    pkey_set(key, PKEY_DISABLE_ACCESS);

    pkey_set(key, 0);                       /* відчинили — одна команда */
    printf("довжина секрету: %zu\n", strlen(secret));
    pkey_set(key, PKEY_DISABLE_ACCESS);     /* зачинили */

    signal(SIGSEGV, SIG_DFL);               /* далі escape вже недійсний */
    pkey_mprotect(secret, (size_t)page_size, PROT_READ | PROT_WRITE, 0);
    pkey_free(key);
    munmap(secret, (size_t)page_size);
}
