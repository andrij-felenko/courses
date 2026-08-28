#define _GNU_SOURCE
#include <fcntl.h>
#include <signal.h>
#include <unistd.h>

#define SIG_READY  (SIGRTMIN + 1)

/* 0 — успіх, -1 з errno — ні */
int arm_fd(int fd)
{
    struct f_owner_ex own = { .type = F_OWNER_TID, .pid = gettid() };

    if (fcntl(fd, F_SETOWN_EX, &own) < 0)    return -1;   /* кому */
    if (fcntl(fd, F_SETSIG, SIG_READY) < 0)  return -1;   /* чим  */

    int fl = fcntl(fd, F_GETFL, 0);
    if (fl < 0) return -1;
    return fcntl(fd, F_SETFL, fl | O_ASYNC | O_NONBLOCK); /* чи слати */
}
