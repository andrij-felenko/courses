struct clone_args {
    __aligned_u64 flags;        /* Прапорці CLONE_* */
    __aligned_u64 pidfd;        /* Вказівник для повернення файлового дескриптора процесу */
    __aligned_u64 child_tid;    /* Вказівник на TID у дочірній пам'яті */
    __aligned_u64 parent_tid;   /* Вказівник на TID у батьківській пам'яті */
    __aligned_u64 exit_signal;  /* Сигнал завершення (SIGCHLD) */
    __aligned_u64 stack;        /* Початок пам'яті стека */
    __aligned_u64 stack_size;   /* Розмір виділеного стека */
    __aligned_u64 tls;          /* Вказівник на сегмент Thread-Local Storage */
    __aligned_u64 set_tid;      /* Масив бажаних PID у вкладених просторах */
    __aligned_u64 set_tid_size; /* Кількість елементів у set_tid */
    __aligned_u64 cgroup;       /* Файловий дескриптор цільової cgroup v2 */
};
