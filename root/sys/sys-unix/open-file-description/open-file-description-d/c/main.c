#include <fcntl.h>
#include <stdio.h>
#include <sys/wait.h>
#include <unistd.h>

int main(void) {
    int fd = open("shared.txt", O_WRONLY | O_CREAT | O_TRUNC, 0644);
    if (fd < 0) {
        perror("open");
        return 1;
    }
    write(fd, "AAAAA", 5);          /* позиція опису: 0 → 5 */

    pid_t pid = fork();
    if (pid == 0) {
        write(fd, "BBBBB", 5);      /* та сама позиція: 5 → 10 */
        printf("дитина бачить позицію %lld\n", (long long)lseek(fd, 0, SEEK_CUR));
        fflush(stdout);             /* _exit не зливає буфери stdio */
        _exit(0);
    }
    wait(NULL);
    printf("батько бачить позицію %lld\n", (long long)lseek(fd, 0, SEEK_CUR));
    return 0;
}
