static void on_notify(int sig) { (void)sig; }   /* тіло не потрібне: будить sigsuspend */

int main(void)
{
    long msgsize = SLOT, maxmsg = slots_for(SLOT);
    struct sigaction sa;
    struct sigevent sev;
    struct mq_attr attr;
    sigset_t block, awake;
    char *buf;
    mqd_t q;

    memset(&sa, 0, sizeof sa);
    sa.sa_handler = on_notify;
    sigemptyset(&sa.sa_mask);
    sigaction(SIGRTMIN, &sa, NULL);             /* SIGRTMIN нічий: не збігається
                                                   ні з бібліотечним, ні з прикладним */
    sigemptyset(&block);
    sigaddset(&block, SIGRTMIN);
    sigprocmask(SIG_BLOCK, &block, &awake);     /* awake — стара маска, без SIGRTMIN */

    q = open_queue(maxmsg, msgsize);
    if (q == (mqd_t)-1) { perror("mq_open"); return 1; }

    /* Буфер мусить бути не менший за mq_msgsize — інакше EMSGSIZE навіть
       на восьмибайтовому «стоп». Розмір питаємо в самої черги: вона могла
       дістатися нам від попереднього запуску з іншим слотом. */
    mq_getattr(q, &attr);
    buf = malloc(attr.mq_msgsize);
    if (!buf) { perror("malloc"); return 1; }

    carry_over(q, buf, attr.mq_msgsize);

    memset(&sev, 0, sizeof sev);
    sev.sigev_notify = SIGEV_SIGNAL;
    sev.sigev_signo  = SIGRTMIN;

    for (;;) {
        if (mq_notify(q, &sev) == -1 && errno != EBUSY) { perror("mq_notify"); return 1; }

        drain(q, buf, attr.mq_msgsize);

        if (dispatch_one()) continue;           /* є робота — і назад по нову порцію */
        sigsuspend(&awake);                     /* сон лише з порожніми полицями */
    }
}
