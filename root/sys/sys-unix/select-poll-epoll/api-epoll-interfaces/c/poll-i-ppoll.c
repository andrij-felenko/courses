#include <poll.h>

int poll(struct pollfd *fds, nfds_t nfds, int timeout);   /* таймаут у мілісекундах */

int ppoll(struct pollfd *fds, nfds_t nfds,
          const struct timespec *tmo_p, const sigset_t *sigmask);

struct pollfd {
    int   fd;        /* дескриптор; від'ємне значення — запис пропустити */
    short events;    /* що просимо — заповнює програма */
    short revents;   /* що сталося — заповнює ядро     */
};
