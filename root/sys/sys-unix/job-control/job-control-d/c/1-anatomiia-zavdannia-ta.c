struct task_struct {
    /* ... */
    pid_t pid;
    struct pid *thread_pid;
    struct signal_struct *signal;
    struct task_struct *group_leader;
    /* ... */
};

struct signal_struct {
    /* ... */
    struct pid *pgrp;       /* Вказівник на PID-структуру групи процесів */
    struct pid *session;    /* Вказівник на PID-структуру сеансу */
    int tty_old_pgrp;       /* Збережений PGID після від'єднання TTY */
    /* ... */
};
