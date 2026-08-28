#include <sys/epoll.h>
#include <sys/random.h>
#include <unistd.h>
#include <errno.h>

/* Системні оголошення Bionic libc у заголовках NDK */
int epoll_create(int size);
int epoll_create1(int flags) __INTRODUCED_IN(21);
ssize_t getrandom(void *buf, size_t buflen, unsigned int flags) __INTRODUCED_IN(28);

/* Безпечний виклик системного API */
int initialize_event_loop(void) {
    /* Якщо __ANDROID_API__ < 21, epoll_create1 буде заблоковано на етапі збірки */
    int fd = epoll_create1(EPOLL_CLOEXEC);
    if (fd < 0) {
        return -errno;
    }
    return fd;
}
