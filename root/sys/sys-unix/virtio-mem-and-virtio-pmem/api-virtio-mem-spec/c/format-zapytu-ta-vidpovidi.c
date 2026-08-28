/* Типи запитів (virtio_mem_req.type) */
#define VIRTIO_MEM_REQ_PLUG           0  /* Підключити діапазон суб-блоків */
#define VIRTIO_MEM_REQ_UNPLUG         1  /* Відключити діапазон суб-блоків */
#define VIRTIO_MEM_REQ_UNPLUG_ALL     2  /* Відключити всі блоки (при скиданні) */
#define VIRTIO_MEM_REQ_STATE          3  /* Запитати стан діапазону блоків */

/* Запит від драйвера гостя */
struct virtio_mem_req {
    __le16 type;        /* VIRTIO_MEM_REQ_* */
    __le16 padding[3];  /* Вирівнювання до 8 байтів */
    union {
        struct {
            __le64 addr;      /* Початкова адреса в просторі GPA */
            __le16 nb_blocks; /* Кількість послідовних суб-блоків */
            __le16 padding[3];
        } state;
        struct {
            __le64 addr;
            __le16 nb_blocks;
            __le16 padding[3];
        } plug;
        struct {
            __le64 addr;
            __le16 nb_blocks;
            __le16 padding[3];
        } unplug;
    } u;
};

/* Статуси відповідей (virtio_mem_resp.type) */
#define VIRTIO_MEM_RESP_ACK           0  /* Операція успішна */
#define VIRTIO_MEM_RESP_NACK          1  /* Відмова (немає ресурсів / помилка) */
#define VIRTIO_MEM_RESP_BUSY          2  /* Пристрій зайнятий, повторити пізніше */
#define VIRTIO_MEM_RESP_ERROR         3  /* Критична помилка виконання */

/* Відповідь від гіпервізора */
struct virtio_mem_resp {
    __le16 type;        /* VIRTIO_MEM_RESP_* */
    __le16 padding[3];
    union {
        struct {
            /* 0 = PLUGGED, 1 = UNPLUGGED, 2 = MIXED (діапазон підключений частково) */
            __le16 state;
        } state;
    } u;
};
