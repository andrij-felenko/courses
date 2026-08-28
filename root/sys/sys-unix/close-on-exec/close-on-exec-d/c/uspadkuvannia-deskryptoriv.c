#include <unistd.h>
#include <fcntl.h>

/* Оболонка готує перенаправлення stdout у файл */
int fd = open("output.txt", O_WRONLY | O_CREAT | O_TRUNC, 0644);
if (fd >= 0) {
    dup2(fd, STDOUT_FILENO); /* тепер дескриптор 1 веде в output.txt */
    close(fd);
    char *argv[] = { "ls", "-la", NULL };
    execve("/bin/ls", argv, NULL); /* ls нічого не знає про файл, але пише в 1 */
}
