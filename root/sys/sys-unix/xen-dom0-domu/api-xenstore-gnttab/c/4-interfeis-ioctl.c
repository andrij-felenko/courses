/* Структура запиту на відображення грантів */
struct ioctl_gntdev_map_grant_ref {
    uint32_t count; /* Кількість грантів у масиві refs */
    uint32_t pad;
    struct ioctl_gntdev_grant_ref {
        uint32_t domid; /* ID домену-власника сторінки (DomU) */
        uint32_t ref;   /* Індекс grant reference (gref) */
    } refs[1];          /* Динамічний масив елементів для пакетного мапування */

    uint64_t index;     /* Вихідне псевдо-зміщення для подальшого виклику mmap() */
};

/* Структура запиту на зняття відображення */
struct ioctl_gntdev_unmap_grant_ref {
    uint64_t index;     /* Зміщення, отримане під час виклику MAP ioctl */
    uint32_t count;     /* Кількість сторінок для unmap */
    uint32_t pad;
};

#define IOCTL_GNTDEV_MAP_GRANT_REF   _IOC(_IOC_NONE, 'G', 0, sizeof(struct ioctl_gntdev_map_grant_ref))
#define IOCTL_GNTDEV_UNMAP_GRANT_REF _IOC(_IOC_NONE, 'G', 1, sizeof(struct ioctl_gntdev_unmap_grant_ref))
