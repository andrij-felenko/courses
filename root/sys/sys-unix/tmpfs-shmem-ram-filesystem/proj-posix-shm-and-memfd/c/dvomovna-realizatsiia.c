#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <errno.h>

/* Створення опечатаного memfd буфера у C */
int create_sealed_buffer(const char *name, size_t size, const char *initial_data) {
    int fd = memfd_create(name, MFD_ALLOW_SEALING | MFD_CLOEXEC);
    if (fd < 0) {
        perror("memfd_create failed");
        return -1;
    }

    if (ftruncate(fd, (off_t)size) < 0) {
        perror("ftruncate failed");
        close(fd);
        return -1;
    }

    void *ptr = mmap(NULL, size, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
    if (ptr == MAP_FAILED) {
        perror("mmap failed");
        close(fd);
        return -1;
    }

    if (initial_data) {
        size_t len = strlen(initial_data);
        if (len > size) len = size;
        memcpy(ptr, initial_data, len);
    }

    /* Завершення запису: знімаємо відображення — інакше F_SEAL_WRITE поверне EBUSY */
    munmap(ptr, size);

    /* Застосування печаток: заборона зміни розміру та подальшого запису */
    if (fcntl(fd, F_ADD_SEALS, F_SEAL_SHRINK | F_SEAL_GROW | F_SEAL_WRITE | F_SEAL_SEAL) < 0) {
        perror("fcntl F_ADD_SEALS failed");
        close(fd);
        return -1;
    }

    return fd;
}

int main(void) {
    const char *payload = "Приклад даних у розділюваній пам'яті shmem/tmpfs";
    size_t buf_size = 4096;

    int memfd = create_sealed_buffer("ipc_shared_buffer", buf_size, payload);
    if (memfd < 0) {
        return EXIT_FAILURE;
    }

    printf("Успішно створено опечатаний memfd дескриптор: %d\n", memfd);

    /* Спроба змінити розмір опечатаного файла поверне помилку EPERM */
    if (ftruncate(memfd, 8192) < 0) {
        printf("Перевірка печатки успішна: ftruncate повернув помилку (errno=%d: %s)\n",
               errno, strerror(errno));
    }

    close(memfd);
    return EXIT_SUCCESS;
}
