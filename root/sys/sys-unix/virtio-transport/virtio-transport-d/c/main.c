/* include/uapi/linux/virtio_ring.h */
struct vring_desc {          /* таблиця дескрипторів: 16 байтів на ланку */
        __virtio64 addr;     /* фізична адреса буфера в пам'яті гостя     */
        __virtio32 len;
        __virtio16 flags;    /* NEXT (ланцюг триває) · WRITE · INDIRECT   */
        __virtio16 next;     /* номер наступної ланки ланцюга             */
};

struct vring_avail {         /* доступне кільце: пише лише драйвер        */
        __virtio16 flags;
        __virtio16 idx;      /* вільно росте, обертається на 2¹⁶          */
        __virtio16 ring[];   /* номери голів ланцюгів                     */
};

struct vring_used_elem { __virtio32 id; __virtio32 len; };

struct vring_used {          /* ужите кільце: пише лише пристрій          */
        __virtio16 flags;
        __virtio16 idx;
        struct vring_used_elem ring[];
};
