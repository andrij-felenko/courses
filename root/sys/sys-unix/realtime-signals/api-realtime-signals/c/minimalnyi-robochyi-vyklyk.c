#define _POSIX_C_SOURCE 200809L
#include <signal.h>
#include <string.h>
#include <time.h>
#include <stdio.h>

/* Номер беруть під час виконання — і звіряють із верхньою межею. */
static int rt_slot(int n)
{
    int sig = SIGRTMIN + n;
    return sig <= SIGRTMAX ? sig : -1;
}

/* Таймер, який принесе назад власну мітку в si_value. */
static int arm_timer(timer_t *tid, int sig, void *tag)
{
    struct sigevent sev;

    memset(&sev, 0, sizeof sev);         /* три останні поля — в об'єднанні */
    sev.sigev_notify = SIGEV_SIGNAL;
    sev.sigev_signo  = sig;
    sev.sigev_value.sival_ptr = tag;     /* приїде в si_value */

    return timer_create(CLOCK_MONOTONIC, &sev, tid);
}

/* Розбір запису: які поля значущі, каже si_code — і тільки він. */
static void describe(const siginfo_t *si)
{
    switch (si->si_code) {          /* si_code — стала, на відміну від SIGRTMIN */
    case SI_QUEUE:
        printf("sigqueue: pid %d, uid %u, вантаж %d\n",
               (int)si->si_pid, (unsigned)si->si_uid, si->si_value.sival_int);
        break;
    case SI_TIMER:
        printf("таймер %p, пропущено %d спрацювань\n",
               si->si_value.sival_ptr, si->si_overrun);
        break;
    case SI_MESGQ:
        printf("черга повідомлень: писав pid %d\n", (int)si->si_pid);
        break;
    case SI_USER:
    case SI_TKILL:
        printf("kill або pthread_kill від pid %d — вантажу немає\n",
               (int)si->si_pid);
        break;
    default:
        printf("код %d: si_value не читаємо\n", si->si_code);
    }
}
