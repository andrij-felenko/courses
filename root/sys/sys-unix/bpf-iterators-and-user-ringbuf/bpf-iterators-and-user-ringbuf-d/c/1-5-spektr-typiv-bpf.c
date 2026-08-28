/* Зчитування BPF-ітератора з користувацького простору (Userspace C) */
#include <stdio.h>
#include <fcntl.h>
#include <unistd.h>

int main(void)
{
    int fd = open("/sys/fs/bpf/my_task_iter", O_RDONLY);
    if (fd < 0) {
        perror("Помилка відкриття BPF-ітератора");
        return 1;
    }

    char buffer[1024];
    ssize_t n;
    while ((n = read(fd, buffer, sizeof(buffer) - 1)) > 0) {
        buffer[n] = '\0';
        printf("%s", buffer);
    }

    close(fd);
    return 0;
}
