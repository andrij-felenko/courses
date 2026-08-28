struct ctl_table {
    const char *procname;         /* Ім'я файлу або каталогу в /proc/sys */
    void *data;                   /* Вказівник на змінну в пам'яті ядра */
    int maxlen;                   /* Максимальний розмір даних у байтах */
    umode_t mode;                 /* Права доступу VFS (наприклад, 0644 або 0444) */
    proc_handler *proc_handler;   /* Обробник читання/запису */
    struct ctl_table_poll *poll;  /* Опціональна підтримка poll/epoll */
    void *extra1;                 /* Додатковий параметр (наприклад, мінімальне значення) */
    void *extra2;                 /* Додатковий параметр (наприклад, максимальне значення) */
};
