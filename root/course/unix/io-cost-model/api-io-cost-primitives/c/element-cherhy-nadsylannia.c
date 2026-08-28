struct io_uring_sqe {
    __u8   opcode;        /* Код операції (IORING_OP_*) */
    __u8   flags;         /* Прапорці поведінки операції (IOSQE_*) */
    __u16  ioprio;        /* Пріоритет вводу-виводу (IOPRIO_PRIO_VALUE) */
    __s32  fd;            /* Файловий дескриптор або індекс фіксованого файлу */
    union {
        __u64  off;       /* Зміщення у файлі (offset) */
        __u64  addr2;     /* Додаткова адреса для операцій типу splice */
    };
    union {
        __u64  addr;      /* Покажчик на буфер або масив struct iovec */
        __u64  splice_off_in;
    };
    __u32  len;           /* Довжина буфера або кількість векторів iovec */
    union {
        __kernel_rwf_t  rw_flags;     /* Прапорці RWF_* для читання/запису */
        __u32           fsync_flags;  /* Прапорці IORING_FSYNC_* */
        __u16           buf_index;    /* Індекс зареєстрованого буфера */
        __u16           buf_group;    /* Група автоматично виділених буферів */
    };
    __u64  user_data;     /* 64-бітний ідентифікатор запиту користувача */
    union {
        struct {
            __u16  buf_index;  /* Індекс буфера */
            __u16  personality;/* Ідентифікатор прав доступу credentials */
            __s32  splice_fd_in;
        };
        __u8   pad2[24];  /* Доповнення структури до 64 байтів */
    };
};
