struct vring_used_elem {
    uint32_t id;   /* Індекс головного дескриптора ланцюжка з Descriptor Table */
    uint32_t len;  /* Кількість записаних у буфер байтів */
};

struct vring_used {
    uint16_t flags;                /* VRING_USED_F_NO_NOTIFY (1 = пригнічення kick) */
    uint16_t idx;                  /* Індекс наступного елемента, який запише vhost */
    struct vring_used_elem ring[N];/* Масив результатів обробки */
    uint16_t avail_event;          /* Вказувач порогу сповіщення */
};
