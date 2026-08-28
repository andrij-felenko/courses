/* Налаштування набору сигналів, які скидаються до SIG_DFL */
int posix_spawnattr_setsigdefault(posix_spawnattr_t *restrict attr,
                                 const sigset_t *restrict sigdefault);

/* Налаштування маски заблокованих сигналів */
int posix_spawnattr_setsigmask(posix_spawnattr_t *restrict attr,
                              const sigset_t *restrict sigmask);

/* Налаштування ідентифікатора цільової групи процесів (PGID) */
int posix_spawnattr_setpgroup(posix_spawnattr_t *attr, pid_t pgroup);

/* Налаштування політики планувальника */
int posix_spawnattr_setschedpolicy(posix_spawnattr_t *attr, int policy);

/* Налаштування пріоритету планувальника */
int posix_spawnattr_setschedparam(posix_spawnattr_t *restrict attr,
                                 const struct sched_param *restrict schedparam);
