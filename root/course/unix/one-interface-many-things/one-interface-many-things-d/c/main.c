#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <sys/stat.h>
#include <sys/socket.h>

void inspect_and_process_descriptor(int fd)
{
    struct stat st;
    if (fstat(fd, &st) == -1) {
        perror("fstat failed");
        return;
    }

    const char *type_name = "невідомий";
    int is_seekable = 0;

    if (S_ISREG(st.st_mode)) {
        type_name = "регулярний файл на диску";
        is_seekable = 1;
    } else if (S_ISSOCK(st.st_mode)) {
        type_name = "мережевий сокет";
    } else if (S_ISFIFO(st.st_mode)) {
        type_name = "канал (pipe/FIFO)";
    } else if (S_ISCHR(st.st_mode)) {
        type_name = "символьний пристрій (char device)";
    } else if (S_ISBLK(st.st_mode)) {
        type_name = "блоковий пристрій (block device)";
        is_seekable = 1;
    }

    printf("Дескриптор %d: тип = %s, inode = %lu\n", fd, type_name, (unsigned long)st.st_ino);

    if (is_seekable) {
        off_t current_pos = lseek(fd, 0, SEEK_CUR);
        if (current_pos != (off_t)-1) {
            printf("  Поточна позиція у файлі: %ld байтів\n", (long)current_pos);
        }
    } else {
        printf("  Позиціювання не підтримується (потоковий ресурс)\n");
    }

    char buffer[256];
    ssize_t bytes_read = read(fd, buffer, sizeof(buffer) - 1);

    if (bytes_read > 0) {
        buffer[bytes_read] = '\0';
        printf("  Прочитано %zd байтів: \"%.*s\"\n", bytes_read, (int)bytes_read, buffer);
    } else if (bytes_read == 0) {
        printf("  Отримано кінець потоку (EOF або закриття з'єднання)\n");
    } else {
        if (errno == EAGAIN || errno == EWOULDBLOCK) {
            printf("  Дані ще не готові (режим O_NONBLOCK)\n");
        } else {
            perror("  Помилка read()");
        }
    }
}
