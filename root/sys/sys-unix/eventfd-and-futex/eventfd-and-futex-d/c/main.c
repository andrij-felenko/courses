#include <sys/eventfd.h>
#include <sys/epoll.h>
#include <unistd.h>
#include <stdint.h>

int efd = eventfd(0, EFD_CLOEXEC | EFD_NONBLOCK);

/* робоча нитка, коли дорахувала: */
uint64_t one = 1;
write(efd, &one, sizeof one);              /* лічильник += 1 */

/* цикл подій, разово: */
struct epoll_event ev = { .events = EPOLLIN, .data.fd = efd };
epoll_ctl(ep, EPOLL_CTL_ADD, efd, &ev);

/* цикл подій, на кожній ітерації: */
if (fired.data.fd == efd) {
    uint64_t n;
    if (read(efd, &n, sizeof n) == (ssize_t)sizeof n)
        collect_results(n);                /* n — скільки разів нас смикнули */
}
