#include <fcntl.h>
#include <stdio.h>
#include <unistd.h>

void demo_write_mechanics(void) {
    /* 1. Рівень stdio: байти осідають у буфері процесу */
    FILE *fp = fopen("app.log", "w");
    if (fp) {
        fputs("Рядок у stdio буфері\n", fp);
        fflush(fp); /* Явний виклик POSIX write() */
        fclose(fp);
    }

    /* 2. Прямий POSIX виклик: оминає stdio, йде в ядро */
    int fd = open("app.log", O_WRONLY | O_APPEND);
    if (fd >= 0) {
        const char msg[] = "Прямий системний виклик\n";
        ssize_t ret = write(fd, msg, sizeof(msg) - 1);
        (void)ret;
        close(fd);
    }
}
