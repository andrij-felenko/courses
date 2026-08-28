union sigval {
    int   sival_int;
    void *sival_ptr;
};

struct sigevent {
    int              sigev_notify;              /* SIGEV_NONE / SIGNAL / THREAD */
    int              sigev_signo;               /* який сигнал                  */
    union sigval     sigev_value;               /* довільне значення програми   */
    void           (*sigev_notify_function)(union sigval);
    pthread_attr_t  *sigev_notify_attributes;   /* NULL — типові атрибути       */
    pid_t            sigev_notify_thread_id;    /* лише POSIX-таймери           */
};
