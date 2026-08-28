/* drivers/virtio/virtio_balloon.c */
struct virtio_balloon {
    struct virtio_device *vdev;
    struct virtqueue *inflate_vq, *deflate_vq, *stats_vq, *free_page_vq;

    /* Список захоплених сторінок, захищений спін-блокуванням */
    struct list_head pages;
    struct balloon_dev_info vb_dev_info;

    /* Робоча черга для виконання операцій надування/здування у фоні */
    struct work_struct update_balloon_size_work;
    struct work_struct update_balloon_stats_work;

    /* Лічильники сторінок */
    size_t num_pages;       /* Цільова кількість сторінок від хоста */
    size_t num_pfns;        /* Поточна кількість елементів у буфері */
    __virtio32 pfns[256];   /* Масив номерів кадрів для передачі */

    /* Механізм зворотного вивільнення при браку пам'яті в гості */
    struct shrinker *shrinker;
};
