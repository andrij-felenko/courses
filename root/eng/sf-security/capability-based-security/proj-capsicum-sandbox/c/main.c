#include <sys/types.h>
#include <sys/capsicum.h>
#include <fcntl.h>
#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <string.h>

#define CHUNK_SIZE 4096

/* Основна функція обробки даних усередині пісочниці */
static int process_stream(int fd_in, int fd_out) {
    char buffer[CHUNK_SIZE];
    ssize_t bytes_read;

    while ((bytes_read = read(fd_in, buffer, sizeof(buffer))) > 0) {
        /* Трансформація: інверсія регістру символів латиниці */
        for (ssize_t i = 0; i < bytes_read; ++i) {
            if (buffer[i] >= 'a' && buffer[i] <= 'z') {
                buffer[i] = (char)(buffer[i] - 32);
            } else if (buffer[i] >= 'A' && buffer[i] <= 'Z') {
                buffer[i] = (char)(buffer[i] + 32);
            }
        }
        
        ssize_t bytes_written = write(fd_out, buffer, (size_t)bytes_read);
        if (bytes_written != bytes_read) {
            return -1;
        }
    }
    return (bytes_read == 0) ? 0 : -1;
}

int main(int argc, char *argv[]) {
    if (argc != 3) {
        fprintf(stderr, "Використання: %s <input_file> <output_file>\n", argv[0]);
        return 1;
    }

    /* 1. Фаза ініціалізації: відкриття файлів до входу в пісочницю */
    int fd_in = open(argv[1], O_RDONLY);
    if (fd_in < 0) {
        perror("Не вдалося відкрити вхідний файл");
        return 1;
    }

    int fd_out = open(argv[2], O_WRONLY | O_CREAT | O_TRUNC, 0644);
    if (fd_out < 0) {
        perror("Не вдалося створити вихідний файл");
        close(fd_in);
        return 1;
    }

    /* 2. Фаза звуження прав: підготовка та застосування масок */
    cap_rights_t rights_in;
    cap_rights_init(&rights_in, CAP_READ, CAP_SEEK, CAP_FSTAT);
    if (cap_rights_limit(fd_in, &rights_in) < 0) {
        perror("Помилка cap_rights_limit для вхідного дескриптора");
        close(fd_in);
        close(fd_out);
        return 1;
    }

    cap_rights_t rights_out;
    cap_rights_init(&rights_out, CAP_WRITE, CAP_SEEK, CAP_FSTAT, CAP_FTRUNCATE);
    if (cap_rights_limit(fd_out, &rights_out) < 0) {
        perror("Помилка cap_rights_limit для вихідного дескриптора");
        close(fd_in);
        close(fd_out);
        return 1;
    }

    /* 3. Фаза ізоляції: вхід у capability mode */
    if (cap_enter() < 0) {
        perror("Помилка виклику cap_enter");
        close(fd_in);
        close(fd_out);
        return 1;
    }

    /* Демонстрація захисту: спроба несанкціонованого доступу до файлової системи */
    int fd_leak = open("/etc/resolv.conf", O_RDONLY);
    if (fd_leak < 0 && errno == ECAPMODE) {
        /* Ядро заблокувало виклик: глобальні шляхи заборонені */
    }

    /* Виконання обчислень у безпечному середовищі */
    int status = process_stream(fd_in, fd_out);

    close(fd_in);
    close(fd_out);
    return (status == 0) ? 0 : 2;
}
