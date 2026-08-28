#include <sys/file.h>
#include <system_error>

/* Взяти виключний замок у C++ */
void lock_exclusive(int fd) {
    while (flock(fd, LOCK_EX) != 0) {
        if (errno == EINTR) continue;
        throw std::system_error(errno, std::generic_category(), "flock LOCK_EX failed");
    }
}

void unlock(int fd) {
    flock(fd, LOCK_UN);
}
