struct tracepoint_func {
    void *func;    /* Покажчик на функцію зворотного виклику */
    void *data;    /* Довільний контекст підписника (ftrace, perf, bpf) */
    int prio;      /* Пріоритет виклику обробника */
};

struct tracepoint {
    const char *name;                      /* Ім'я точки трасування (наприклад, "sched_switch") */
    struct static_key_false key;           /* Керуючий Static Key */
    struct static_call_key *static_call_key;
    void *static_call_tramp;
    void *iterator;
    int (*regfunc)(void);                  /* Опціональний хук при першій реєстрації підписника */
    void (*unregfunc)(void);               /* Опціональний хук при видаленні останнього підписника */
    struct tracepoint_func __rcu *funcs;   /* Масив зареєстрованих обробників під захистом RCU */
};
