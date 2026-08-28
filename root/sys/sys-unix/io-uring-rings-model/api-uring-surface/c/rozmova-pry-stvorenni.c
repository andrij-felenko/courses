struct io_uring_params {
    __u32 sq_entries;                  /* ← ядро: скільки SQE виділено насправді */
    __u32 cq_entries;                  /* ⇄ з CQSIZE — прохання; без нього — відповідь */
    __u32 flags;                       /* → IORING_SETUP_*                        */
    __u32 sq_thread_cpu;               /* → з SQ_AFF: до якого ядра прив'язати потік */
    __u32 sq_thread_idle;              /* → з SQPOLL: скільки мс простою до засинання */
    __u32 features;                    /* ← ядро: IORING_FEAT_* — що воно вміє    */
    __u32 wq_fd;                       /* → з ATTACH_WQ: чиї робітники позичаємо  */
    __u32 resv[3];                     /* → мусить бути нулем                     */
    struct io_sqring_offsets sq_off;   /* ← де що лежить у відображенні SQ        */
    struct io_cqring_offsets cq_off;   /* ← те саме для CQ                        */
};

struct io_sqring_offsets {
    __u32 head, tail;          /* лічильники: голову рухає ядро, хвіст — програма */
    __u32 ring_mask;           /* розмір − 1: індекс = лічильник & ring_mask       */
    __u32 ring_entries;
    __u32 flags;               /* IORING_SQ_NEED_WAKEUP і решта                    */
    __u32 dropped;             /* скільки SQE ядро відкинуло як зіпсовані          */
    __u32 array;               /* масив індексів у масив SQE                       */
    __u32 resv1;
    __u64 user_addr;           /* із IORING_SETUP_NO_MMAP — адреса від програми    */
};

struct io_cqring_offsets {
    __u32 head, tail;          /* тут навпаки: хвіст рухає ядро, голову — програма */
    __u32 ring_mask;
    __u32 ring_entries;
    __u32 overflow;            /* скільки завершень втрачено зовсім (не врятував  */
                               /* навіть список переповнення)                     */
    __u32 cqes;                /* самі записи CQE — у цьому ж відображенні         */
    __u32 flags;
    __u32 resv1;
    __u64 user_addr;
};
