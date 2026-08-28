#include <mqueue.h>
#include <signal.h>
#include <fcntl.h>
#include <stdlib.h>
#include <errno.h>
#include <stdio.h>

static void on_msg(int sig) { (void)sig; }          /* тіло не потрібне */
void handle(const char *msg, size_t len, unsigned prio);

int main(void)
{
    struct sigaction sa = { .sa_handler = on_msg };
    sigemptyset(&sa.sa_mask);
    sigaction(SIGUSR1, &sa, NULL);

    /* сигнал блокуємо: інакше він може прийти між читанням і засинанням */
    sigset_t blocked, waiting;
    sigemptyset(&blocked);
    sigaddset(&blocked, SIGUSR1);
    sigprocmask(SIG_BLOCK, &blocked, &waiting);     /* waiting — маска без SIGUSR1 */

    mqd_t q = mq_open("/drive-cmd", O_RDONLY | O_NONBLOCK);
    if (q == (mqd_t)-1) { perror("mq_open"); return 1; }

    struct mq_attr attr;
    mq_getattr(q, &attr);
    char *buf = malloc(attr.mq_msgsize);

    struct sigevent ev = { .sigev_notify = SIGEV_SIGNAL, .sigev_signo = SIGUSR1 };

    for (;;) {
        if (mq_notify(q, &ev) == -1 && errno != EBUSY) { perror("mq_notify"); return 1; }

        for (;;) {                                  /* вичерпуємо все наявне */
            unsigned prio;
            ssize_t n = mq_receive(q, buf, attr.mq_msgsize, &prio);
            if (n == -1) {
                if (errno == EAGAIN) break;         /* порожньо — можна спати */
                perror("mq_receive"); return 1;
            }
            handle(buf, (size_t)n, prio);
        }

        sigsuspend(&waiting);                       /* відпустити сигнал і заснути — атомарно */
    }
}
