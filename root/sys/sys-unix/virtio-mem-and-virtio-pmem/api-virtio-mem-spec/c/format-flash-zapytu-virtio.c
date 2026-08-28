#define VIRTIO_PMEM_REQ_TYPE_FLUSH   0  /* Скинути кеші файлу / накопичувача хоста */

/* Структура запиту у віртчерзі */
struct virtio_pmem_req {
    __le32 type;        /* VIRTIO_PMEM_REQ_TYPE_FLUSH */
};

/* Структура відповіді від хоста */
struct virtio_pmem_resp {
    __le32 ret;         /* 0 = успіх; будь-яке інше значення драйвер віддає гостю як -EIO */
};
