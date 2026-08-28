struct vdpa_vq_state_split {
    u16 avail_index; /* Поточний індекс доступних дескрипторів */
};

struct vdpa_vq_state_packed {
    u16 last_avail_idx; /* Індекс доступного дескриптора у кільці */
    u16 last_used_idx;  /* Індекс використаного дескриптора */
    u8  avail_counter;  /* Однобітовий прапор фази доступності */
    u8  used_counter;   /* Однобітовий прапор фази використання */
};

struct vdpa_vq_state {
    union {
        struct vdpa_vq_state_split split;
        struct vdpa_vq_state_packed packed;
    };
};
