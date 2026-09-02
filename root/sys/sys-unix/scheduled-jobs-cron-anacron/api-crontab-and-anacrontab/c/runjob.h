/* Конвеєр запуску завдання: fork, ізоляція сесії, зниження привілеїв,
   захоплення виводу та поштовий звіт через MTA. */
#ifndef MINICRON_RUNJOB_H
#define MINICRON_RUNJOB_H

typedef struct {
    const char *user;       /* від чийого імені виконувати */
    const char *command;    /* рядок для «$SHELL -c» */
    const char *stdin_data; /* усе після першого незахищеного '%' або NULL */
    const char *mailto;     /* NULL або "" — пошта вимкнена */
    const char *shell;      /* NULL — /bin/sh */
    char *const *envp;      /* NULL-завершене середовище завдання */
} cron_job_t;

/* Повертає код завершення команди (або 128+сигнал), -1 — не вдалося запустити. */
int cron_job_run(const cron_job_t *job);

#endif /* MINICRON_RUNJOB_H */
