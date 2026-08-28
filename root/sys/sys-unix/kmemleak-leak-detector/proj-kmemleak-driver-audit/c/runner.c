/* runner.c — C11 інструмент для автоматизації сканування Kmemleak */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <stdbool.h>

#define KMEMLEAK_PATH "/sys/kernel/debug/kmemleak"
#define BUF_SIZE 8192

static bool write_cmd(const char *cmd) {
    int fd = open(KMEMLEAK_PATH, O_WRONLY);
    if (fd < 0) {
        perror("Помилка відкриття " KMEMLEAK_PATH " для запису");
        return false;
    }
    ssize_t len = strlen(cmd);
    if (write(fd, cmd, len) != len) {
        perror("Помилка відправки команди у kmemleak");
        close(fd);
        return false;
    }
    close(fd);
    return true;
}

int main(void) {
    printf("[+] Очищення попередніх звітів kmemleak...\n");
    if (!write_cmd("clear\n")) return EXIT_FAILURE;

    printf("[+] Симуляція дій: завантаження та вивантаження модуля...\n");
    if (system("modprobe dummy_leak_driver 2>/dev/null || insmod ./dummy_leak_driver.ko") != 0) {
        fprintf(stderr, "[-] Не вдалося завантажити модуль\n");
        return EXIT_FAILURE;
    }
    sleep(1);
    system("rmmod dummy_leak_driver");

    printf("[+] Ініціація примусового сканування (scan)...\n");
    if (!write_cmd("scan\n")) return EXIT_FAILURE;

    printf("[+] Читання результатів аудіювання...\n");
    int fd = open(KMEMLEAK_PATH, O_RDONLY);
    if (fd < 0) {
        perror("Помилка відкриття kmemleak для читання");
        return EXIT_FAILURE;
    }

    char buffer[BUF_SIZE];
    ssize_t bytes_read = read(fd, buffer, sizeof(buffer) - 1);
    close(fd);

    if (bytes_read <= 0) {
        printf("[SUCCESS] Витоків пам'яті не виявлено!\n");
        return EXIT_SUCCESS;
    }

    buffer[bytes_read] = '\0';
    printf("[WARNING] ЗНАЙДЕНО ВИ ТІК ПАМ'ЯТІ:\n%s\n", buffer);
    return EXIT_FAILURE;
}
