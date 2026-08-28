#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <errno.h>
#include <stdint.h>
#include <drm/drm.h>

/* Допоміжна функція зчитання sysfs-атрибута */
static int read_sysfs_attr(const char *path, char *buf, size_t size) {
    int fd = open(path, O_RDONLY);
    if (fd < 0) return -1;
    ssize_t bytes = read(fd, buf, size - 1);
    close(fd);
    if (bytes < 0) return -1;
    buf[bytes] = '\0';
    /* Видаляємо символ нового рядка */
    char *newline = strchr(buf, '\n');
    if (newline) *newline = '\0';
    return 0;
}

int main(void) {
    int fd = open("/dev/accel/accel0", O_RDWR | O_CLOEXEC);
    if (fd < 0) {
        perror("Не вдалося відкрити /dev/accel/accel0");
        return EXIT_FAILURE;
    }

    /* 1. Запит версії драйвера через DRM_IOCTL_VERSION */
    char name[32] = {0};
    char date[32] = {0};
    char desc[64] = {0};

    struct drm_version ver = {
        .name_len = sizeof(name) - 1,
        .name = name,
        .date_len = sizeof(date) - 1,
        .date = date,
        .desc_len = sizeof(desc) - 1,
        .desc = desc,
    };

    if (ioctl(fd, DRM_IOCTL_VERSION, &ver) < 0) {
        perror("Помилка DRM_IOCTL_VERSION");
        close(fd);
        return EXIT_FAILURE;
    }

    printf("Драйвер Accel: %s (%s), опис: %s\n", ver.name, ver.date, ver.desc);

    /* 2. Зчитання атрибутів з sysfs */
    char temp_buf[32] = {0};
    char usage_buf[32] = {0};
    if (read_sysfs_attr("/sys/class/accel/accel0/device/temperature", temp_buf, sizeof(temp_buf)) == 0) {
        printf("Температура NPU: %s mC\n", temp_buf);
    }
    if (read_sysfs_attr("/sys/class/accel/accel0/device/engine_usage", usage_buf, sizeof(usage_buf)) == 0) {
        printf("Завантаження NPU: %s%%\n", usage_buf);
    }

    /* 3. Створення об'єкта синхронізації syncobj */
    struct drm_syncobj_create create_sync = {
        .flags = DRM_SYNCOBJ_CREATE_SIGNALED,
    };

    if (ioctl(fd, DRM_IOCTL_SYNCOBJ_CREATE, &create_sync) < 0) {
        perror("Помилка DRM_IOCTL_SYNCOBJ_CREATE");
        close(fd);
        return EXIT_FAILURE;
    }

    printf("Успішно створено syncobj, handle: %u\n", create_sync.handle);

    /* 4. Очищення об'єкта syncobj */
    struct drm_syncobj_destroy destroy_sync = {
        .handle = create_sync.handle,
    };
    ioctl(fd, DRM_IOCTL_SYNCOBJ_DESTROY, &destroy_sync);

    close(fd);
    return EXIT_SUCCESS;
}
