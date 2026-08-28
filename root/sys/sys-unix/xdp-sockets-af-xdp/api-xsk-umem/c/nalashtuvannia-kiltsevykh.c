struct xdp_ring_offset {
    __u64 producer;     /* Зсув до атомарного індексу виробника */
    __u64 consumer;     /* Зсув до атомарного індексу споживача */
    __u64 descriptors;  /* Зсув до масиву дескрипторів кадру */
    __u64 flags;        /* Зсув до прапорців стану кільця (наприклад, XDP_RING_NEED_WAKEUP) */
};

struct xdp_mmap_offsets {
    struct xdp_ring_offset rx;
    struct xdp_ring_offset tx;
    struct xdp_ring_offset fr; /* Fill Ring */
    struct xdp_ring_offset cr; /* Completion Ring */
};
