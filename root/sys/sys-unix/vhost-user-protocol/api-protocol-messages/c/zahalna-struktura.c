/* Двійковий заголовок та універсальний конверт повідомлення vhost-user */
struct vhost_user_msg {
    uint32_t request;          /* Код запиту або відповіді (опкод) */
    uint32_t flags;            /* Бітові прапорці версії, напрямку та підтвердження */
    uint32_t size;             /* Розмір корисного навантаження (payload) у байтах */
    union {
        uint64_t u64;
        struct vhost_user_vring_state state;
        struct vhost_user_vring_addr addr;
        struct vhost_user_memory memory;
        struct vhost_user_log log;
        struct vhost_user_config config;
        struct vhost_user_inflight inflight;
        uint8_t raw[1024];
    } payload;
} __attribute__((packed));
