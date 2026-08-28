/* include/uapi/linux/virtio_pci.h */
struct virtio_pci_cap {
        __u8   cap_vndr;    /* 0x09 — PCI_CAP_ID_VNDR, запис виробника */
        __u8   cap_next;
        __u8   cap_len;
        __u8   cfg_type;    /* яка саме структура — таблиця нижче      */
        __u8   bar;         /* у якому вікні BAR вона лежить, 0–5      */
        __u8   id;          /* коли таких структур кілька              */
        __u8   padding[2];
        __le32 offset;      /* зсув усередині вікна                    */
        __le32 length;
};

struct virtio_pci_notify_cap {
        struct virtio_pci_cap cap;
        __le32 notify_off_multiplier;
};
