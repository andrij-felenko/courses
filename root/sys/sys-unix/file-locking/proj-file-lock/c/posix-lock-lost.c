/* posix-lock-lost.c — cc -Wall -o posix-lock-lost posix-lock-lost.c */
#define _GNU_SOURCE
#include <fcntl.h>
#include <stdio.h>
#include <sys/wait.h>
#include <unistd.h>

/* Чи може ЧУЖИЙ процес узяти замок на цей файл прямо зараз?
   Так — означає, що наш замок більше не існує.                      */
static int file_is_free(const char *path)
{
    struct flock fl = { .l_type = F_WRLCK, .l_whence = SEEK_SET,
                        .l_start = 0, .l_len = 0 };
    int st;
    pid_t pid = fork();

    if (pid == 0) {
        int fd = open(path, O_RDWR);
        _exit(fd >= 0 && fcntl(fd, F_SETLK, &fl) == 0 ? 0 : 1);
    }
    waitpid(pid, &st, 0);
    return WEXITSTATUS(st) == 0;
}

int main(void)
{
    const char *path = "/var/tmp/demo.db";
    struct flock fl = { .l_type = F_WRLCK, .l_whence = SEEK_SET,
                        .l_start = 0, .l_len = 0 };
    int fd = open(path, O_RDWR | O_CREAT, 0644);
    int other;

    if (fcntl(fd, F_SETLK, &fl) != 0) { perror("F_SETLK"); return 1; }
    printf("замок узято:          файл вільний? %s\n",
           file_is_free(path) ? "так" : "ні");

    other = open(path, O_RDONLY);   /* «стороння бібліотека дивиться розмір» */
    close(other);                   /* саме цей рядок і знімає ваш замок */

    printf("після чужого close:   файл вільний? %s\n",
           file_is_free(path) ? "так" : "ні");
    return 0;
}
