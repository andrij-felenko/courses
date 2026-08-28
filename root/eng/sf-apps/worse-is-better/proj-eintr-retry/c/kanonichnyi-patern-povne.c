#include <unistd.h>
#include <errno.h>
#include <stddef.h>

// Повне надійне читання: гарантує зчитування count байтів або повідомляє про EOF/помилку
ssize_t read_exact(int fd, void *buf, size_t count) {
    size_t total_read = 0;
    char *p = (char *)buf;

    while (total_read < count) {
        ssize_t res = read(fd, p + total_read, count - total_read);
        if (res == -1) {
            if (errno == EINTR) {
                // Перервано сигналом до передачі байтів у цій ітерації — повторюємо
                continue;
            }
            // Справжня фатальна помилка введення-виведення
            return -1;
        }
        if (res == 0) {
            // Несподіваний кінець потоку (EOF)
            break;
        }
        total_read += (size_t)res;
    }
    return (ssize_t)total_read;
}

// Повний надійний запис: гарантує надсилання всіх count байтів навіть при частинних передачах
ssize_t write_exact(int fd, const void *buf, size_t count) {
    size_t total_written = 0;
    const char *p = (const char *)buf;

    while (total_written < count) {
        ssize_t res = write(fd, p + total_written, count - total_written);
        if (res == -1) {
            if (errno == EINTR) {
                // Перервано сигналом — повторюємо спробу з поточної позиції
                continue;
            }
            // Справжня фатальна помилка
            return -1;
        }
        if (res == 0) {
            // Канал чи сокет не приймає дані
            break;
        }
        total_written += (size_t)res;
    }
    return (ssize_t)total_written;
}
