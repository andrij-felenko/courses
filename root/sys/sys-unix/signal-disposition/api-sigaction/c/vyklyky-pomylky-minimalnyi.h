int sigaction(int signum, const struct sigaction *act, struct sigaction *oldact);
int sigprocmask(int how, const sigset_t *set, sigset_t *oldset);      /* однопотокова програма */
int pthread_sigmask(int how, const sigset_t *set, sigset_t *oldset);  /* багатопотокова        */

int sigemptyset(sigset_t *set);        /* набір ОБОВ'ЯЗКОВО спорожнити або заповнити */
int sigfillset(sigset_t *set);         /* перед першим sigaddset                     */
int sigaddset(sigset_t *set, int signum);
int sigdelset(sigset_t *set, int signum);
int sigismember(const sigset_t *set, int signum);   /* 1 — є, 0 — нема, -1 — помилка */

/* how для (pthread_)sigprocmask: SIG_BLOCK | SIG_UNBLOCK | SIG_SETMASK */

int sigaltstack(const stack_t *ss, stack_t *old_ss);       /* стек для SA_ONSTACK */
int sigqueue(pid_t pid, int sig, const union sigval value); /* сигнал зі значенням */
