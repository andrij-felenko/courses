struct sigevent {
    int             sigev_notify;               /* SIGEV_* — спосіб сповістити */
    int             sigev_signo;                /* номер сигналу */
    union sigval    sigev_value;                /* прийде в si_value чи в аргументі функції */
    void          (*sigev_notify_function)(union sigval);
    pthread_attr_t *sigev_notify_attributes;
    pid_t           sigev_notify_thread_id;     /* лише Linux */
};

union sigval {
    int   sival_int;
    void *sival_ptr;
};
