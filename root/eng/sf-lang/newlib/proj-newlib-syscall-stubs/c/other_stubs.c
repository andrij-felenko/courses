/**
 * @file other_stubs.c
 * @brief Реалізація допоміжних системних заглушок Newlib (C99)
 */
#include "syscall_stubs.h"
#include <errno.h>
#include <sys/stat.h>
#include <sys/reent.h>

int _close_r(struct _reent *r, int fd) {
    if (fd >= 0 && fd <= 2) {
        return 0; /* Стандартні потоки не закриваються */
    }
    r->_errno = EBADF;
    return -1;
}

int _close(int fd) {
    return _close_r(_impure_ptr, fd);
}

int _fstat_r(struct _reent *r, int fd, struct stat *st) {
    if (st == NULL) {
        r->_errno = EINVAL;
        return -1;
    }

    if (fd >= 0 && fd <= 2) {
        st->st_mode = S_IFCHR; /* Символьний пристрій */
        st->st_blksize = 0;
        return 0;
    }

    r->_errno = EBADF;
    return -1;
}

int _fstat(int fd, struct stat *st) {
    return _fstat_r(_impure_ptr, fd, st);
}

int _isatty_r(struct _reent *r, int fd) {
    if (fd >= 0 && fd <= 2) {
        return 1; /* Дескриптори 0, 1, 2 є терміналом TTY */
    }
    r->_errno = EBADF;
    return 0;
}

int _isatty(int fd) {
    return _isatty_r(_impure_ptr, fd);
}

off_t _lseek_r(struct _reent *r, int fd, off_t offset, int whence) {
    (void)offset;
    (void)whence;
    if (fd >= 0 && fd <= 2) {
        r->_errno = ESPIPE; /* Послідовний термінал не підтримує seek */
        return (off_t)-1;
    }
    r->_errno = EBADF;
    return (off_t)-1;
}

off_t _lseek(int fd, off_t offset, int whence) {
    return _lseek_r(_impure_ptr, fd, offset, whence);
}

pid_t _getpid_r(struct _reent *r) {
    (void)r;
    return 1; /* Єдиний фіктивний процес у системі */
}

pid_t _getpid(void) {
    return 1;
}

int _kill_r(struct _reent *r, pid_t pid, int sig) {
    (void)pid;
    (void)sig;
    r->_errno = EINVAL;
    return -1;
}

int _kill(pid_t pid, int sig) {
    return _kill_r(_impure_ptr, pid, sig);
}

void _exit(int status) {
    (void)status;
    /* Вимикаємо глобальні переривання процесора */
    __asm__ volatile ("cpsid i");

    /* Зациклюємося або викликаємо програмне перезавантаження через SCB->AIRCR */
    while (1) {
        __asm__ volatile ("wfi"); /* Sleep mode */
    }
}
