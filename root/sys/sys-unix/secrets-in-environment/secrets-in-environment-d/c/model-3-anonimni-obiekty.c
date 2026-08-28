/* Створення запечатаного секретного буфера через memfd_create мовою C */
#define _GNU_SOURCE
#include <sys/mman.h>
#include <unistd.h>
#include <fcntl.h>
#include <string.h>
#include <stdio.h>

int create_sealed_secret_fd(const char *secret, size_t len) {
    /* Створюємо анонімний дескриптор пам'яті з дозволом пломбування */
    int fd = memfd_create("secure_secret_blob", MFD_CLOEXEC | MFD_ALLOW_SEALING);
    if (fd < 0) {
        perror("memfd_create");
        return -1;
    }

    /* Виділяємо необхідний розмір та записуємо секрет */
    if (ftruncate(fd, (off_t)len) < 0) {
        perror("ftruncate");
        close(fd);
        return -1;
    }

    if (write(fd, secret, len) != (ssize_t)len) {
        perror("write");
        close(fd);
        return -1;
    }

    /* Накладаємо незворотні пломби: заборона запису, стиснення, розширення та зміни пломб */
    if (fcntl(fd, F_ADD_SEALS, F_SEAL_WRITE | F_SEAL_SHRINK | F_SEAL_GROW | F_SEAL_SEAL) < 0) {
        perror("fcntl F_ADD_SEALS");
        close(fd);
        return -1;
    }

    /* Повертаємо покажчик читання на початок */
    lseek(fd, 0, SEEK_SET);
    return fd;
}
