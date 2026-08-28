/* gem_dumb_prime.c - Виділення та експорт GEM буфера мовою C */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <xf86drm.h>
#include <xf86drmMode.h>

#define WIDTH  640
#define HEIGHT 480
#define BPP    32

int main(void)
{
    int drm_fd = -1;
    int prime_fd = -1;
    int client_fd = -1;
    uint8_t *map_ptr = MAP_FAILED;
    struct drm_mode_create_dumb create_req;
    struct drm_mode_map_dumb map_req;
    struct drm_mode_destroy_dumb destroy_req;
    struct drm_prime_handle prime_req;
    int ret = 0;

    /* 1. Відкриваємо основний пристрій DRM */
    drm_fd = open("/dev/dri/card0", O_RDWR | O_CLOEXEC);
    if (drm_fd < 0) {
        perror("Помилка відкриття /dev/dri/card0");
        return EXIT_FAILURE;
    }

    /* 2. Запитуємо створення лінійного dumb-буфера */
    memset(&create_req, 0, sizeof(create_req));
    create_req.width = WIDTH;
    create_req.height = HEIGHT;
    create_req.bpp = BPP;

    if (ioctl(drm_fd, DRM_IOCTL_MODE_CREATE_DUMB, &create_req) < 0) {
        perror("DRM_IOCTL_MODE_CREATE_DUMB завершився помилкою");
        ret = EXIT_FAILURE;
        goto cleanup_fd;
    }

    printf("[DRM] Створено GEM буфер: хендл=%u, розмір=%llu байтів, pitch=%u байтів\n",
           create_req.handle, (unsigned long long)create_req.size, create_req.pitch);

    /* 3. Отримуємо фальшиве зміщення (fake offset) для виклику mmap */
    memset(&map_req, 0, sizeof(map_req));
    map_req.handle = create_req.handle;

    if (ioctl(drm_fd, DRM_IOCTL_MODE_MAP_DUMB, &map_req) < 0) {
        perror("DRM_IOCTL_MODE_MAP_DUMB завершився помилкою");
        ret = EXIT_FAILURE;
        goto cleanup_buffer;
    }

    printf("[DRM] Отримано фальшиве зміщення ядра: 0x%llx\n",
           (unsigned long long)map_req.offset);

    /* 4. Відображаємо сторінки буфера в адресний простір процесу */
    map_ptr = (uint8_t *)mmap(NULL, create_req.size, PROT_READ | PROT_WRITE,
                              MAP_SHARED, drm_fd, (off_t)map_req.offset);
    if (map_ptr == MAP_FAILED) {
        perror("mmap завершився помилкою");
        ret = EXIT_FAILURE;
        goto cleanup_buffer;
    }

    /* 5. Заповнюємо буфер градієнтом (формат XRGB8888) */
    for (uint32_t y = 0; y < HEIGHT; ++y) {
        uint32_t *row = (uint32_t *)(map_ptr + y * create_req.pitch);
        for (uint32_t x = 0; x < WIDTH; ++x) {
            uint8_t r = (uint8_t)((x * 255) / WIDTH);
            uint8_t g = (uint8_t)((y * 255) / HEIGHT);
            uint8_t b = 128;
            row[x] = (0xFF << 24) | (r << 16) | (g << 8) | b;
        }
    }
    printf("[CPU] Буфер успішно заповнено графічним градієнтом.\n");

    /* 6. Експортуємо GEM-хендл у файловий дескриптор dma-buf (PRIME) */
    memset(&prime_req, 0, sizeof(prime_req));
    prime_req.handle = create_req.handle;
    prime_req.flags = DRM_CLOEXEC | DRM_RDWR;

    if (ioctl(drm_fd, DRM_IOCTL_PRIME_HANDLE_TO_FD, &prime_req) < 0) {
        perror("DRM_IOCTL_PRIME_HANDLE_TO_FD завершився помилкою");
        ret = EXIT_FAILURE;
        goto cleanup_mmap;
    }
    prime_fd = prime_req.fd;
    printf("[PRIME] Буфер експортовано в dma-buf fd=%d\n", prime_fd);

    /* 7. Емулюємо імпорт дескриптора у вторинному клієнтському контексті */
    client_fd = open("/dev/dri/card0", O_RDWR | O_CLOEXEC);
    if (client_fd >= 0) {
        struct drm_prime_handle import_req;
        memset(&import_req, 0, sizeof(import_req));
        import_req.fd = prime_fd;

        if (ioctl(client_fd, DRM_IOCTL_PRIME_FD_TO_HANDLE, &import_req) == 0) {
            printf("[Клієнт] Успішно імпортовано dma-buf: локальний хендл=%u\n",
                   import_req.handle);

            /* Закриваємо імпортований локальний хендл */
            struct drm_gem_close close_req = { .handle = import_req.handle, .pad = 0 };
            ioctl(client_fd, DRM_IOCTL_GEM_CLOSE, &close_req);
        }
        close(client_fd);
    }

cleanup_mmap:
    if (map_ptr != MAP_FAILED) {
        munmap(map_ptr, create_req.size);
    }
    if (prime_fd >= 0) {
        close(prime_fd);
    }

cleanup_buffer:
    memset(&destroy_req, 0, sizeof(destroy_req));
    destroy_req.handle = create_req.handle;
    if (ioctl(drm_fd, DRM_IOCTL_MODE_DESTROY_DUMB, &destroy_req) < 0) {
        perror("DRM_IOCTL_MODE_DESTROY_DUMB помилка");
    } else {
        printf("[DRM] Dumb-буфер успішно звільнено в ядрі.\n");
    }

cleanup_fd:
    close(drm_fd);
    return ret;
}
