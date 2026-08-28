/**
 * @file other_stubs.cpp
 * @brief Реалізація допоміжних системних заглушок Newlib (C++20)
 */
#include "syscall_stubs.hpp"
#include <cerrno>
#include <sys/stat.h>
#include <sys/reent.h>

extern "C" {

auto _close_r(struct _reent *r, int fd) noexcept -> int {
    if (fd >= 0 && fd <= 2) {
        return 0;
    }
    r->_errno = EBADF;
    return -1;
}

auto _close(int fd) noexcept -> int {
    return _close_r(_impure_ptr, fd);
}

auto _fstat_r(struct _reent *r, int fd, struct stat *st) noexcept -> int {
    if (st == nullptr) {
        r->_errno = EINVAL;
        return -1;
    }
    if (fd >= 0 && fd <= 2) {
        st->st_mode = S_IFCHR;
        st->st_blksize = 0;
        return 0;
    }
    r->_errno = EBADF;
    return -1;
}

auto _fstat(int fd, struct stat *st) noexcept -> int {
    return _fstat_r(_impure_ptr, fd, st);
}

auto _isatty_r(struct _reent *r, int fd) noexcept -> int {
    if (fd >= 0 && fd <= 2) {
        return 1;
    }
    r->_errno = EBADF;
    return 0;
}

auto _isatty(int fd) noexcept -> int {
    return _isatty_r(_impure_ptr, fd);
}

auto _lseek_r(struct _reent *r, int fd, off_t /*offset*/, int /*whence*/) noexcept -> off_t {
    if (fd >= 0 && fd <= 2) {
        r->_errno = ESPIPE;
        return static_cast<off_t>(-1);
    }
    r->_errno = EBADF;
    return static_cast<off_t>(-1);
}

auto _lseek(int fd, off_t offset, int whence) noexcept -> off_t {
    return _lseek_r(_impure_ptr, fd, offset, whence);
}

auto _getpid_r(struct _reent* /*r*/) noexcept -> pid_t {
    return 1;
}

auto _getpid() noexcept -> pid_t {
    return 1;
}

auto _kill_r(struct _reent *r, pid_t /*pid*/, int /*sig*/) noexcept -> int {
    r->_errno = EINVAL;
    return -1;
}

auto _kill(pid_t pid, int sig) noexcept -> int {
    return _kill_r(_impure_ptr, pid, sig);
}

[[noreturn]] void _exit(int /*status*/) noexcept {
    asm volatile ("cpsid i");
    while (true) {
        asm volatile ("wfi");
    }
}

} // extern "C"
