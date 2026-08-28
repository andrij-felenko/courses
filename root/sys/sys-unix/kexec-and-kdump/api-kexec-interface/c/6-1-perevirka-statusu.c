#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>

int check_kexec_status(void) {
    int fd = open("/sys/kernel/kexec_loaded", O_RDONLY);
    if (fd < 0) {
        perror("Не вдалося відкрити /sys/kernel/kexec_loaded");
        return -1;
    }

    char buf[8] = {0};
    ssize_t bytes_read = read(fd, buf, sizeof(buf) - 1);
    close(fd);

    if (bytes_read > 0) {
        int loaded = atoi(buf);
        printf("Статус завантаження kexec: %d\n", loaded);
        return loaded;
    }

    return -1;
}

int main(void) {
    check_kexec_status();
    return 0;
}
