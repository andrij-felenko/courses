/* pmsafe.c — читати файл на постійній пам'яті й пережити збійну комірку. */
#define _GNU_SOURCE          /* BUS_MCEERR_*, si_addr_lsb, FALLOC_FL_PUNCH_HOLE */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <errno.h>
#include <fcntl.h>
#include <unistd.h>
#include <setjmp.h>
#include <signal.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <sys/ioctl.h>
#include <sys/sysmacros.h>
#include <linux/fs.h>
#include <linux/fiemap.h>

/* Безпечна точка — своя на кожен потік: сигнал від апаратного збою приходить
   саме тому потокові, який торкнувся комірки, і стрибати він мусить у свій
   кадр, а не в чужий. */
static __thread sigjmp_buf safe_point;
static __thread volatile sig_atomic_t guarded;  /* вікно відкрите */
static __thread volatile sig_atomic_t f_code;   /* si_code */
static __thread volatile sig_atomic_t f_lsb;    /* si_addr_lsb */
static __thread void *volatile        f_addr;   /* si_addr */

static void on_sigbus(int sig, siginfo_t *si, void *uc)
{
    (void)sig; (void)uc;

    if (!guarded) {
        /* Збій поза охоронюваним вікном: стрибати нікуди, а повертатися не
           можна. write і _exit — з переліку дозволеного в обробнику. */
        static const char m[] = "pmsafe: SIGBUS поза вікном\n";
        ssize_t r = write(2, m, sizeof m - 1);
        (void)r;
        _exit(135);                       /* 128 + SIGBUS */
    }

    /* Звичайні присвоєння тут безпечні не тому, що вони атомарні, а тому, що
       перерваний код більше не виконуватиметься: читати ці поля будуть уже
       після стрибка, у звичайному контексті того самого потоку. */
    f_addr = si->si_addr;
    f_code = si->si_code;
    f_lsb  = si->si_addr_lsb ? si->si_addr_lsb : 12;
    guarded = 0;
    siglongjmp(safe_point, 1);
}

static int arm_sigbus(void)
{
    struct sigaction sa;
    memset(&sa, 0, sizeof sa);
    sa.sa_sigaction = on_sigbus;
    sa.sa_flags = SA_SIGINFO;   /* без нього не буде ні si_addr, ні si_code */
    sigemptyset(&sa.sa_mask);
    return sigaction(SIGBUS, &sa, NULL);
}

/* Копія з відображення під охороною: 0 — прочитано, -1 — збій, і тоді в f_*
   лежить усе, що приніс сигнал.

   Те, що sigsetjmp стоїть у крихітній окремій функції, — не косметика.
   Локальні змінні функції, яка кликала sigsetjmp, після стрибка мають
   невизначені значення, якщо їх міняли й не позначили volatile. Тут міняти
   нічого: стрибок веде в кадр pm_copy, а той одразу повертає -1 звичайним
   поверненням — і цикл нагорі бачить просто невдалий виклик. */
static int pm_copy(void *dst, const void *src, size_t n)
{
    guarded = 1;
    if (sigsetjmp(safe_point, 1) != 0)  /* 1 — маску сигналів теж відновити */
        return -1;
    memcpy(dst, src, n);
    guarded = 0;
    return 0;
}
