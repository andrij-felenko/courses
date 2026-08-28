#define _GNU_SOURCE
#include <unistd.h>
#include <fcntl.h>
#include <stdio.h>
#include <errno.h>

int release_open_file_space(pid_t pid, int target_fd) {
    char proc_path[64];
    snprintf(proc_path, sizeof(proc_path), "/proc/%d/fd/%d", pid, target_fd);

    /* Відкриваємо дескриптор файлу через procfs */
    int fd = open(proc_path, O_WRONLY);
    if (fd < 0) {
        perror("Не вдалося відкрити procfs дескриптор");
        return -1;
    }

    /* Метод 1: Скидання розміру до 0 */
    if (ftruncate(fd, 0) != 0) {
        perror("Помилка ftruncate");
        close(fd);
        return -1;
    }

    /* Метод 2 (альтернатива для сумісних ФС): деалокація блоків через fallocate */
    #ifdef FALLOC_FL_PUNCH_HOLE
    fallocate(fd, FALLOC_FL_PUNCH_HOLE | FALLOC_FL_KEEP_SIZE, 0, 1024 * 1024 * 1024);
    #endif

    close(fd);
    return 0;
}
