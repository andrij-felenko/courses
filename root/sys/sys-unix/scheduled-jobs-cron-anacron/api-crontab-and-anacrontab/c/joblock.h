/* Ексклюзивний замок завдання: захист від накладання двох запусків. */
#ifndef MINICRON_JOBLOCK_H
#define MINICRON_JOBLOCK_H

typedef enum {
    JOB_LOCK_HELD  = 0,  /* замок наш, дескриптор у out_fd */
    JOB_LOCK_BUSY  = 1,  /* попередній запуск ще працює */
    JOB_LOCK_ERROR = -1  /* системна помилка, текст уже в stderr */
} job_lock_status_t;

/* Дескриптор треба тримати відкритим увесь час роботи завдання. */
job_lock_status_t job_lock_acquire(const char *lock_file_path, int *out_fd);

/* Закриття дескриптора і є зняттям замка: ядро звільняє його саме, зокрема й
   тоді, коли процес помер від SIGKILL. Завислих замків не буває. */
void job_lock_release(int fd);

#endif /* MINICRON_JOBLOCK_H */
