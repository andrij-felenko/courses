/* privtrap.c — питає процесор про власний рівень і ловить його відмови.
 * Linux, x86-64.  Збірка:  cc -O2 -o privtrap privtrap.c
 */
#define _GNU_SOURCE
#include <setjmp.h>
#include <signal.h>
#include <stdio.h>
#include <string.h>

static sigjmp_buf resume;                   /* куди вертатися після пастки */
static volatile sig_atomic_t got_signo;     /* що прилетіло */
static volatile sig_atomic_t got_code;
static volatile unsigned long produced;     /* що команда встигла повернути */

/* Обробник. Друкувати тут не можна: в обробнику дозволені лише
   async-signal-safe виклики, а printf до них не належить. */
static void on_trap(int signo, siginfo_t *si, void *uctx)
{
    (void)uctx;
    got_signo = signo;
    got_code  = si->si_code;
    siglongjmp(resume, 1);   /* просте return запустило б ту саму команду наново */
}

/* CPL — два молодші біти селектора CS. Читати CS дозволено з будь-якого кільця. */
static unsigned cpl(void)
{
    unsigned short cs;
    __asm__ volatile ("mov %%cs, %0" : "=r"(cs));
    return cs & 3u;
}

/* Піддослідні команди. volatile — щоб оптимізатор не викинув те,
   що з його погляду не має видимого наслідку. */
static void t_nop  (void) { __asm__ volatile ("nop"); }
static void t_hlt  (void) { __asm__ volatile ("hlt"); }
static void t_cli  (void) { __asm__ volatile ("cli"); }
static void t_cr0  (void) { unsigned long v;
                            __asm__ volatile ("mov %%cr0, %0" : "=r"(v));
                            produced = v; }
static void t_rdmsr(void) { unsigned int lo, hi;
                            __asm__ volatile ("rdmsr" : "=a"(lo), "=d"(hi)
                                                      : "c"(0xC0000080u));
                            produced = ((unsigned long)hi << 32) | lo; }
static void t_smsw (void) { unsigned short w;
                            __asm__ volatile ("smsw %0" : "=r"(w));
                            produced = w; }
static void t_sldt (void) { unsigned short s;
                            __asm__ volatile ("sldt %0" : "=r"(s));
                            produced = s; }
static void t_ud2  (void) { __asm__ volatile ("ud2"); }

struct probe { const char *mnem; void (*run)(void); const char *what; };

static void try_one(const struct probe *p)
{
    got_signo = 0;
    produced  = 0;
    if (sigsetjmp(resume, 1) == 0) {     /* 1 — зберегти й відновити маску сигналів */
        p->run();
        printf("  %-6s виконано, результат 0x%lx   (%s)\n",
               p->mnem, produced, p->what);
    } else {
        printf("  %-6s пастка: %s, si_code=%d   (%s)\n", p->mnem,
               strsignal((int)got_signo), (int)got_code, p->what);
    }
}

int main(void)
{
    static const struct probe probes[] = {
        { "nop",   t_nop,   "звичайна команда — контрольний дослід" },
        { "hlt",   t_hlt,   "спинити процесор" },
        { "cli",   t_cli,   "вимкнути переривання" },
        { "cr0",   t_cr0,   "прочитати керівний регістр CR0" },
        { "rdmsr", t_rdmsr, "прочитати машинний регістр EFER" },
        { "smsw",  t_smsw,  "прочитати молодші 16 бітів CR0 (спадок 80286)" },
        { "sldt",  t_sldt,  "прочитати селектор локальної таблиці дескрипторів" },
        { "ud2",   t_ud2,   "завжди невизначена команда — для порівняння" },
    };
    struct sigaction sa;
    size_t i;

    printf("рівень привілею цього процесу: CPL = %u\n\n", cpl());

    memset(&sa, 0, sizeof sa);
    sa.sa_sigaction = on_trap;
    sa.sa_flags     = SA_SIGINFO;
    sigemptyset(&sa.sa_mask);
    sigaction(SIGSEGV, &sa, NULL);   /* сюди Linux переводить #GP */
    sigaction(SIGILL,  &sa, NULL);   /* а сюди — #UD */

    for (i = 0; i < sizeof probes / sizeof probes[0]; i++)
        try_one(&probes[i]);
    return 0;
}
