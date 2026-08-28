struct io_sqring_offsets {
    __u32 head;        /* Зміщення вказівника голови SQ */
    __u32 tail;        /* Зміщення вказівника хвоста SQ */
    __u32 ring_mask;   /* Маска розміру буфера (entries - 1) */
    __u32 ring_entries;/* Кількість елементів у SQ */
    __u32 flags;       /* Прапорці стану SQ (наприклад, IORING_SQ_NEED_WAKEUP) */
    __u32 dropped;     /* Лічильник відкинутих SQE (коли SQ переповнена) */
    __u32 array;       /* Зміщення масиву індексів SQE */
    __u32 resv1;
    __u64 resv2;
};

struct io_cqring_offsets {
    __u32 head;        /* Зміщення вказівника голови CQ */
    __u32 tail;        /* Зміщення вказівника хвоста CQ */
    __u32 ring_mask;   /* Маска розміру буфера CQ */
    __u32 ring_entries;/* Кількість елементів у CQ */
    __u32 overflow;    /* Лічильник втрачених CQE через переповнення черги */
    __u32 cqes;        /* Зміщення масиву структур io_uring_cqe */
    __u32 flags;
    __u32 resv1;
    __u64 resv2;
};
