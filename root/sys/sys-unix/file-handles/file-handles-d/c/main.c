#define _GNU_SOURCE
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

int main(void)
{
    struct file_handle *fh = malloc(sizeof(*fh) + MAX_HANDLE_SZ);
    int mount_id, mfd, fd;
    char buf[64];
    ssize_t n;

    fh->handle_bytes = MAX_HANDLE_SZ;
    if (name_to_handle_at(AT_FDCWD, "index.log", fh, &mount_id, 0) < 0) {
        perror("name_to_handle_at");
        return 1;
    }
    printf("тип %d, байтів %u, монтування %d\n",
           fh->handle_type, fh->handle_bytes, mount_id);

    /* ім'я більше не має значення */
    if (rename("index.log", "arch/2026-08/index.log") < 0) {
        perror("rename");
        return 1;
    }

    /* дескриптор потрібен лише щоб назвати файлову систему —
       годиться будь-що на тій самій ФС, де лежить наш файл */
    mfd = open(".", O_RDONLY | O_DIRECTORY);
    if (mfd < 0) { perror("open ."); return 1; }

    fd = open_by_handle_at(mfd, fh, O_RDONLY);
    if (fd < 0) { perror("open_by_handle_at"); return 1; }

    n = read(fd, buf, sizeof(buf) - 1);
    if (n > 0) { buf[n] = '\0'; printf("прочитано: %s", buf); }
    return 0;
}
