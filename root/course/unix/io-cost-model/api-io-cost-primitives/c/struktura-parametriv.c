struct io_uring_params {
    __u32 sq_entries;         /* Розмір черги надсилання (повертає ядро) */
    __u32 cq_entries;         /* Розмір черги завершення (зазвичай 2 * sq_entries) */
    __u32 flags;              /* Прапорці конфігурації рушія (IORING_SETUP_*) */
    __u32 sq_thread_cpu;      /* Номер процесорного ядра для потоку SQPOLL */
    __u32 sq_thread_idle;     /* Час простою потоку ядра в мс до засинання */
    __u32 features;           /* Бітова маска підтримуваних функцій ядра */
    __u32 wq_fd;              /* Дескриптор існуючого екземпляра для об'єднання пулу */
    __u32 resv[3];            /* Зарезервовані поля */
    struct io_sqring_offsets sq_off; /* Зміщення полів SQ для виклику mmap */
    struct io_cqring_offsets cq_off; /* Зміщення полів CQ для виклику mmap */
};
