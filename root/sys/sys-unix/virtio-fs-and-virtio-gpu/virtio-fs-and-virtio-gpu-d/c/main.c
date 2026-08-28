#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>

/* Перевірка стану пристрою virtio_gpu через sysfs */
void check_virtio_gpu_sysfs(void) {
    int fd = open("/sys/class/drm/card0/device/vendor", O_RDONLY);
    if (fd < 0) {
        perror("Не вдалося відкрити sysfs картку DRM");
        return;
    }
    char buf[32] = {0};
    ssize_t n = read(fd, buf, sizeof(buf) - 1);
    close(fd);
    if (n <= 0) {
        fprintf(stderr, "Порожнє або нечитне значення vendor\n");
        return;
    }

    printf("Virtio GPU Vendor ID: %s", buf);
}
