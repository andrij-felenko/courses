/* include/uapi/drm/drm_mode.h */
#define DRM_IOCTL_MODE_CREATE_DUMB DRM_IOWR(0xB2, struct drm_mode_create_dumb)
#define DRM_IOCTL_MODE_MAP_DUMB    DRM_IOWR(0xB3, struct drm_mode_map_dumb)
#define DRM_IOCTL_MODE_DESTROY_DUMB DRM_IOWR(0xB4, struct drm_mode_destroy_dumb)

struct drm_mode_create_dumb {
    __u32 height;      /* Вхід: висота в пікселях */
    __u32 width;       /* Вхід: ширина в пікселях */
    __u32 bpp;         /* Вхід: глибина кольору (біт на піксель, наприклад 32) */
    __u32 flags;       /* Вхід: службові прапорці (зазвичай 0) */
    __u32 handle;      /* Вихід: призначений числовий хендл GEM */
    __u32 pitch;       /* Вихід: довжина рядка в байтах із вирівнюванням */
    __u64 size;        /* Вихід: повний виділений розмір буфера в байтах */
};

struct drm_mode_map_dumb {
    __u32 handle;      /* Вхід: числовий хендл GEM-об'єкта */
    __u32 pad;         /* Вирівнювання структури */
    __u64 offset;      /* Вихід: фальшиве зміщення (fake offset) для mmap */
};

struct drm_mode_destroy_dumb {
    __u32 handle;      /* Вхід: числовий хендл буфера для знищення */
};
