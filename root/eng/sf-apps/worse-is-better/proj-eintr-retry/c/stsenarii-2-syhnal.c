#include <unistd.h>
#include <errno.h>

// НЕБЕЗПЕЧНИЙ КОД: втрачає дані під час часткового запису!
ssize_t broken_write_all(int fd, const void *buf, size_t count) {
    ssize_t written;
    do {
        // Якщо записано 32 КБ із 1 МБ, виклик поверне 32768 і вийде з циклу,
        // хоча 968 КБ залишилися незаписаними!
        written = write(fd, buf, count);
    } while (written == -1 && errno == EINTR);
    return written;
}
