/* gbm-kms-pipeline.c — виділення буфера з модифікаторами та імпорт у KMS */
#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <inttypes.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <xf86drm.h>
#include <xf86drmMode.h>
#include <gbm.h>
#include <drm_fourcc.h>

/* Структура для зберігання зареєстрованого кадрового буфера KMS */
struct kms_framebuffer {
    uint32_t fb_id;
    uint32_t width;
    uint32_t height;
    uint32_t format;
    uint64_t modifier;
    int plane_fds[4];
    uint32_t plane_count;
};

/* Створення буфера через GBM та імпорт у KMS */
int create_tiled_kms_fb(int drm_fd, struct gbm_device *gbm,
                        uint32_t width, uint32_t height,
                        uint32_t format, const uint64_t *modifiers,
                        uint32_t mod_count, struct kms_framebuffer *out_fb)
{
    if (!gbm || !modifiers || mod_count == 0 || !out_fb) {
        return -EINVAL;
    }

    memset(out_fb, 0, sizeof(*out_fb));
    for (int i = 0; i < 4; i++) {
        out_fb->plane_fds[i] = -1;
    }

    /* 1. Виділення буфера в GPU з переліком дозволених модифікаторів */
    struct gbm_bo *bo = gbm_bo_create_with_modifiers2(
        gbm, width, height, format, modifiers, mod_count,
        GBM_BO_USE_RENDERING | GBM_BO_USE_SCANOUT
    );

    if (!bo) {
        fprintf(stderr, "Помилка gbm_bo_create_with_modifiers2: %s\n", strerror(errno));
        return -errno;
    }

    uint64_t chosen_mod = gbm_bo_get_modifier(bo);
    int plane_count = gbm_bo_get_plane_count(bo);
    if (plane_count <= 0 || plane_count > 4) {
        fprintf(stderr, "Некоректна кількість площин буфера: %d\n", plane_count);
        gbm_bo_destroy(bo);
        return -EINVAL;
    }

    uint32_t handles[4] = {0};
    uint32_t strides[4] = {0};
    uint32_t offsets[4] = {0};
    uint64_t mods[4] = {0};

    /* 2. Отримання дескрипторів dma-buf та геометрії для кожної площини */
    for (int p = 0; p < plane_count; p++) {
        int fd = gbm_bo_get_fd_for_plane(bo, p);
        if (fd < 0) {
            fprintf(stderr, "Помилка експорту dma-buf для площини %d: %s\n", p, strerror(errno));
            for (int i = 0; i < p; i++) {
                if (out_fb->plane_fds[i] >= 0) close(out_fb->plane_fds[i]);
            }
            gbm_bo_destroy(bo);
            return -errno;
        }

        out_fb->plane_fds[p] = fd;
        strides[p] = gbm_bo_get_stride_for_plane(bo, p);
        offsets[p] = gbm_bo_get_offset(bo, p);
        mods[p] = chosen_mod;

        /* Імпорт dma-buf FD як GEM-хендлу для цього пристрою DRM */
        int ret = drmPrimeFDToHandle(drm_fd, fd, &handles[p]);
        if (ret < 0) {
            fprintf(stderr, "Помилка drmPrimeFDToHandle для площини %d: %s\n", p, strerror(errno));
            for (int i = 0; i <= p; i++) {
                if (out_fb->plane_fds[i] >= 0) close(out_fb->plane_fds[i]);
            }
            gbm_bo_destroy(bo);
            return ret;
        }
    }

    /* 3. Реєстрація кадрового буфера у KMS з явними модифікаторами */
    uint32_t fb_id = 0;
    int ret = drmModeAddFB2WithModifiers(
        drm_fd, width, height, format,
        handles, strides, offsets, mods,
        &fb_id, DRM_MODE_FB_MODIFIERS
    );

    /* Закриваємо локальні GEM-хендли (KMS FB утримує власні посилання ядра) */
    for (int p = 0; p < plane_count; p++) {
        struct drm_gem_close req = { .handle = handles[p] };
        drmIoctl(drm_fd, DRM_IOCTL_GEM_CLOSE, &req);
    }

    if (ret < 0) {
        fprintf(stderr, "Помилка drmModeAddFB2WithModifiers: %s (код %d)\n", strerror(errno), ret);
        for (int p = 0; p < plane_count; p++) {
            if (out_fb->plane_fds[p] >= 0) close(out_fb->plane_fds[p]);
        }
        gbm_bo_destroy(bo);
        return ret;
    }

    /* Зберігаємо результати у вихідну структуру */
    out_fb->fb_id = fb_id;
    out_fb->width = width;
    out_fb->height = height;
    out_fb->format = format;
    out_fb->modifier = chosen_mod;
    out_fb->plane_count = plane_count;

    printf("Створено KMS FB #%u: %ux%u, format=0x%08x, mod=0x%016" PRIx64 ", площин=%u\n",
           fb_id, width, height, format, chosen_mod, plane_count);

    /* Звільняємо тимчасовий об'єкт GBM (буфер утримується через dma-buf та KMS FB) */
    gbm_bo_destroy(bo);
    return 0;
}

/* Звільнення кадрового буфера */
void free_kms_fb(int drm_fd, struct kms_framebuffer *fb)
{
    if (!fb || fb->fb_id == 0) return;

    drmModeRmFB(drm_fd, fb->fb_id);
    for (uint32_t i = 0; i < fb->plane_count; i++) {
        if (fb->plane_fds[i] >= 0) {
            close(fb->plane_fds[i]);
            fb->plane_fds[i] = -1;
        }
    }
    fb->fb_id = 0;
}
