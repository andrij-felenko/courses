/* Таблиця завдань оболонки: облік груп процесів, збір статусів нащадків
 * і передача керівного термінала між оболонкою та завданням.
 */
#ifndef JOBS_H
#define JOBS_H

#include <signal.h>
#include <stdbool.h>
#include <sys/types.h>

#define JOBS_MAX       16
#define JOB_PROCS_MAX   8
#define JOB_TEXT_MAX  256

enum proc_state {
    PROC_RUNNING = 0,
    PROC_STOPPED,
    PROC_DONE
};

struct proc {
    pid_t pid;
    enum proc_state state;
    int status;                    /* сирий статус із waitpid() */
};

struct job {
    bool used;
    int id;
    pid_t pgid;                    /* PID лідера групи = PGID усього конвеєра */
    bool foreground;
    bool notified;                 /* про зупинку/завершення вже сказано користувачу */
    char text[JOB_TEXT_MAX];       /* як завдання виглядало в командному рядку */
    struct proc procs[JOB_PROCS_MAX];
    int nprocs;
};

/* Готує оболонку до керування завданнями: ігнорує термінальні сигнали,
 * запам'ятовує режим термінала й ставить обробник SIGCHLD.
 * tty_fd < 0 або не термінал — керування завданнями вимикається. */
void jobs_init(int tty_fd);

struct job *job_new(bool foreground, const char *text);
void job_drop(struct job *j);
bool job_add_proc(struct job *j, pid_t pid);

/* Оновлює стан процесу за статусом із waitpid(); викликається з обробника. */
void update_job_status(pid_t pid, int status);

bool job_is_done(const struct job *j);
bool job_is_stopped(const struct job *j);

/* Чекає, доки пріоритетне завдання завершиться або зупиниться,
 * повертає термінал оболонці й віддає код виходу. */
int job_wait_foreground(struct job *j);

void jobs_wait_all(void);          /* чекає на всі фонові завдання */
void jobs_report(void);            /* друкує й прибирає завершені фонові завдання */
bool jobs_any_active(void);

void jobs_block_sigchld(sigset_t *saved);
void jobs_restore_mask(const sigset_t *saved);

void give_terminal_to(pid_t pgid);
void take_terminal_back(void);
int  jobs_tty_fd(void);

#endif /* JOBS_H */
