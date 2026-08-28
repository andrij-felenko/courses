#include <unistd.h>
#include <fcntl.h>
#include <stdio.h>
#include <string.h>

int main(void)
{
    const char msg[] = "HELLO\n";
    pid_t pid = getpid();

    printf("PID тестового процесу: %d\n", pid);
    printf("Натисніть Enter для запису в TTY (stdout)...\n");
    getchar();

    /* 1. Запис у термінал (псевдоконсоль) */
    ssize_t ret_tty = write(STDOUT_FILENO, msg, sizeof(msg) - 1);
    if (ret_tty < 0) {
        perror("write tty");
        return 1;
    }

    printf("Натисніть Enter для запису у файл на диску (/tmp/trace_test.txt)...\n");
    getchar();

    /* 2. Запис у звичайний файл на диску */
    int fd_file = open("/tmp/trace_test.txt", O_WRONLY | O_CREAT | O_TRUNC, 0644);
    if (fd_file < 0) {
        perror("open file");
        return 1;
    }

    ssize_t ret_file = write(fd_file, msg, sizeof(msg) - 1);
    if (ret_file < 0) {
        perror("write file");
        close(fd_file);
        return 1;
    }

    close(fd_file);
    printf("Запис завершено успішно (TTY: %zd Б, Диск: %zd Б).\n", ret_tty, ret_file);
    return 0;
}
