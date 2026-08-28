/* include/uapi/linux/virtio_balloon.h */
struct virtio_balloon_stat {
    __virtio16 tag;   /* Ідентифікатор метрики */
    __virtio64 val;   /* Значення лічильника в байтах або кількості подій */
} __attribute__((packed));

/* Теги метрик пам'яті */
#define VIRTIO_BALLOON_S_SWAP_IN       0   /* Кількість байтів, прочитаних зі свопу */
#define VIRTIO_BALLOON_S_SWAP_OUT      1   /* Кількість байтів, записаних у своп */
#define VIRTIO_BALLOON_S_MAJFLT        2   /* Кількість важких помилок сторінки (Major Faults) */
#define VIRTIO_BALLOON_S_MINFLT        3   /* Кількість легких помилок сторінки (Minor Faults) */
#define VIRTIO_BALLOON_S_MEMFREE       4   /* Повністю вільна пам'ять (MemFree у байтах) */
#define VIRTIO_BALLOON_S_MEMTOT        5   /* Загальний обсяг фізичної пам'яті гостя (MemTotal) */
#define VIRTIO_BALLOON_S_AVAIL         6   /* Доступна пам'ять без виклику свопу (MemAvailable) */
#define VIRTIO_BALLOON_S_CACHES        7   /* Дисковий кеш і буфери сторінок (Cached + Buffers) */
#define VIRTIO_BALLOON_S_HTLB_ALLOC    8   /* Кількість успішно виділених HugePages */
#define VIRTIO_BALLOON_S_HTLB_FAIL     9   /* Кількість невдалих спроб виділити HugePages */
#define VIRTIO_BALLOON_S_OOM_KILL     10   /* Лічильник спрацьовувань гостьового OOM Killer */
