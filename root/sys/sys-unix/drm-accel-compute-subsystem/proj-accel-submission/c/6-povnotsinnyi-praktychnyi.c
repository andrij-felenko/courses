#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <string.h>
#include <errno.h>
#include <stdint.h>
#include <drm/drm.h>

/* Спрощені структури UAPI для створення, картографування та подання GEM */
struct accel_gem_create {
    uint64_t size;
    uint32_t handle;
    uint32_t pad;
};

struct accel_gem_mmap {
    uint32_t handle;
    uint32_t pad;
    uint64_t offset;
};

struct accel_command_desc {
    uint32_t handle;
    uint32_t size;
    uint64_t offset;
};

struct accel_submit {
    uint64_t cmds_ptr;
    uint32_t cmd_count;
    uint32_t out_syncobj;
    uint64_t flags;
};

#define DRM_IOCTL_ACCEL_GEM_CREATE  DRM_IOWR(DRM_COMMAND_BASE + 0x01, struct accel_gem_create)
#define DRM_IOCTL_ACCEL_GEM_MMAP    DRM_IOWR(DRM_COMMAND_BASE + 0x02, struct accel_gem_mmap)
#define DRM_IOCTL_ACCEL_SUBMIT      DRM_IOWR(DRM_COMMAND_BASE + 0x03, struct accel_submit)

int main(void) {
    int fd = open("/dev/accel/accel0", O_RDWR | O_CLOEXEC);
    if (fd < 0) {
        perror("Не вдалося відкрити /dev/accel/accel0");
        return EXIT_FAILURE;
    }

    /* 1. Створення GEM-буфера для даних (тензорів) */
    struct accel_gem_create data_req = { .size = 4096 };
    if (ioctl(fd, DRM_IOCTL_ACCEL_GEM_CREATE, &data_req) < 0) {
        perror("Помилка створення GEM-буфера даних");
        close(fd);
        return EXIT_FAILURE;
    }

    /* 2. Створення GEM-буфера для команд NPU */
    struct accel_gem_create cmd_req = { .size = 4096 };
    if (ioctl(fd, DRM_IOCTL_ACCEL_GEM_CREATE, &cmd_req) < 0) {
        perror("Помилка створення GEM-буфера команд");
        close(fd);
        return EXIT_FAILURE;
    }

    /* 3. Картографування буферів у простір адреси процесу */
    struct accel_gem_mmap mmap_data = { .handle = data_req.handle };
    ioctl(fd, DRM_IOCTL_ACCEL_GEM_MMAP, &mmap_data);
    void *data_ptr = mmap(NULL, 4096, PROT_READ | PROT_WRITE, MAP_SHARED, fd, (off_t)mmap_data.offset);

    struct accel_gem_mmap mmap_cmd = { .handle = cmd_req.handle };
    ioctl(fd, DRM_IOCTL_ACCEL_GEM_MMAP, &mmap_cmd);
    void *cmd_ptr = mmap(NULL, 4096, PROT_READ | PROT_WRITE, MAP_SHARED, fd, (off_t)mmap_cmd.offset);

    if (data_ptr == MAP_FAILED || cmd_ptr == MAP_FAILED) {
        perror("Помилка mmap буферів");
        close(fd);
        return EXIT_FAILURE;
    }

    /* Заповнюємо буфер даних тестовим тензором */
    memset(data_ptr, 0x7E, 4096);
    /* Заповнюємо командний буфер умовним нопом / інструкцією NPU */
    memset(cmd_ptr, 0x00, 4096);

    /* 4. Створення об'єкта синхронізації syncobj */
    struct drm_syncobj_create sync_create = { .flags = 0 };
    if (ioctl(fd, DRM_IOCTL_SYNCOBJ_CREATE, &sync_create) < 0) {
        perror("Помилка DRM_IOCTL_SYNCOBJ_CREATE");
        close(fd);
        return EXIT_FAILURE;
    }

    /* 5. Формування та подання завдання CS */
    struct accel_command_desc cmd_desc = {
        .handle = cmd_req.handle,
        .size = 4096,
        .offset = 0,
    };

    struct accel_submit submit_req = {
        .cmds_ptr = (uint64_t)(uintptr_t)&cmd_desc,
        .cmd_count = 1,
        .out_syncobj = sync_create.handle,
        .flags = 0,
    };

    if (ioctl(fd, DRM_IOCTL_ACCEL_SUBMIT, &submit_req) < 0) {
        perror("Помилка подання обчислювального завдання DRM_IOCTL_ACCEL_SUBMIT");
        close(fd);
        return EXIT_FAILURE;
    }

    printf("Подання команд успішно відправлено на NPU. Очікування syncobj...\n");

    /* 6. Очікування завершення виконання на NPU */
    struct drm_syncobj_wait wait_req = {
        .handles = (uint64_t)(uintptr_t)&sync_create.handle,
        .timeout_nsec = 5000000000ULL, /* 5 секунд */
        .count_handles = 1,
        .flags = DRM_SYNCOBJ_WAIT_FLAGS_WAIT_ALL,
        .first_signaled = 0,
        .pad = 0,
    };

    if (ioctl(fd, DRM_IOCTL_SYNCOBJ_WAIT, &wait_req) < 0) {
        perror("Помилка або таймаут DRM_IOCTL_SYNCOBJ_WAIT");
    } else {
        printf("Обчислення на NPU успішно завершено! Перевірка даних тензора...\n");
    }

    /* 7. Очищення ресурсів */
    struct drm_syncobj_destroy sync_destroy = { .handle = sync_create.handle };
    ioctl(fd, DRM_IOCTL_SYNCOBJ_DESTROY, &sync_destroy);

    struct drm_gem_close close_data = { .handle = data_req.handle };
    struct drm_gem_close close_cmd = { .handle = cmd_req.handle };
    ioctl(fd, DRM_IOCTL_GEM_CLOSE, &close_data);
    ioctl(fd, DRM_IOCTL_GEM_CLOSE, &close_cmd);

    munmap(data_ptr, 4096);
    munmap(cmd_ptr, 4096);
    close(fd);

    return EXIT_SUCCESS;
}
