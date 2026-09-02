#include "joblock.h"

#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <string.h>
#include <sys/file.h>
#include <unistd.h>

job_lock_status_t job_lock_acquire(const char *lock_file_path, int *out_fd)
{
    *out_fd = -1;

    /* O_CLOEXEC: замок належить нашому процесові, а не команді, яку ми
       запустимо через exec, — інакше він жив би, доки живе будь-який нащадок. */
    int fd = open(lock_file_path, O_RDWR | O_CREAT | O_CLOEXEC, 0600);
    if (fd < 0) {
        fprintf(stderr, "minicron: open %s: %s\n", lock_file_path, strerror(errno));
        return JOB_LOCK_ERROR;
    }

    /* LOCK_NB: не чекаємо в черзі. Чекати тут означало б назбирати за ніч
       десяток процесів, які прокинуться разом і поб'ються за диск. */
    if (flock(fd, LOCK_EX | LOCK_NB) != 0) {
        const int saved_errno = errno;
        close(fd);
        if (saved_errno == EWOULDBLOCK) {
            return JOB_LOCK_BUSY;
        }
        fprintf(stderr, "minicron: flock %s: %s\n", lock_file_path, strerror(saved_errno));
        return JOB_LOCK_ERROR;
    }

    /* Вміст файлу на замок не впливає — це суто підказка адміністраторові,
       який побачить файл у /var/lock і захоче знати, хто його тримає. */
    char line[32];
    int len = snprintf(line, sizeof line, "%ld\n", (long)getpid());
    if (len > 0 && (ftruncate(fd, 0) != 0 || write(fd, line, (size_t)len) != len)) {
        fprintf(stderr, "minicron: не вдалося записати PID у %s: %s\n",
                lock_file_path, strerror(errno));
    }

    *out_fd = fd;
    return JOB_LOCK_HELD;
}

void job_lock_release(int fd)
{
    if (fd >= 0) {
        close(fd);
    }
}
