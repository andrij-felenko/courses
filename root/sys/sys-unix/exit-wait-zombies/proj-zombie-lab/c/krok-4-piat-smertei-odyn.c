static volatile sig_atomic_t chld_hits;
static volatile sig_atomic_t rt_hits;

static void on_chld(int sig) { (void)sig; chld_hits++; }
static void on_rt(int sig)   { (void)sig; rt_hits++;   }

static int lab_burst(int n)
{
    if (n < 1 || n > 64) n = 5;

    struct sigaction sa;
    memset(&sa, 0, sizeof sa);
    sigemptyset(&sa.sa_mask);
    sa.sa_handler = on_chld;  sigaction(SIGCHLD,  &sa, NULL);
    sa.sa_handler = on_rt;    sigaction(SIGRTMIN, &sa, NULL);

    sigset_t block, old;
    sigemptyset(&block);
    sigaddset(&block, SIGCHLD);
    sigaddset(&block, SIGRTMIN);
    sigprocmask(SIG_BLOCK, &block, &old);          /* двері зачинено */

    pid_t kids[64];
    for (int i = 0; i < n; i++) {
        kids[i] = fork();
        if (kids[i] < 0) { perror("fork"); return 1; }
        if (kids[i] == 0) {
            union sigval v; v.sival_int = i;
            sigqueue(getppid(), SIGRTMIN, v);      /* контрольний зразок */
            _exit(0);
        }
    }
    for (int i = 0; i < n; i++)
        wait_until_zombie(kids[i]);                /* усі n мертві, сигнали за дверима */

    sigset_t pend;
    sigpending(&pend);
    printf("померло дітей: %d\n", n);
    printf("SIGCHLD відкладено: %s\n",
           sigismember(&pend, SIGCHLD) ? "так — один-єдиний біт" : "ні");

    sigprocmask(SIG_SETMASK, &old, NULL);          /* двері відчинено */
    for (int i = 0; i < 200 && rt_hits < n; i++)
        sleep_ms(1);                               /* доганяємо чергу RT-сигналів */

    printf("обробник SIGCHLD спрацював разів:  %d\n", (int)chld_hits);
    printf("обробник SIGRTMIN спрацював разів: %d\n", (int)rt_hits);

    int reaped = 0, status;
    while (waitpid(-1, &status, WNOHANG) > 0)
        reaped++;
    printf("прибрано одним циклом WNOHANG: %d\n", reaped);
    return 0;
}
