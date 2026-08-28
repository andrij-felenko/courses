struct io_uring_sqe {
    __u8   opcode;     /* IORING_OP_URING_CMD = 46 */
    __u8   flags;      /* IOSQE_FIXED_FILE, IOSQE_ASYNC, IOSQE_CQE_SKIP_SUCCESS */
    __u16  ioprio;     /* Пріоритет виконання I/O (ioprio_set) */
    __s32  fd;         /* Файловий дескриптор символьного пристрою /dev/ngXnY */
    union {
        __u64  off;
        __u64  addr2;
        struct {           /* саме тут лежить cmd_op при IORING_OP_URING_CMD */
            __u32  cmd_op; /* код підкоманди драйвера (NVME_URING_CMD_*) */
            __u32  __pad1;
        };
    };
    union {
        __u64  addr;
        __u64  splice_off_in;
    };
    __u32  len;
    __u32  op_flags;   /* Прапорці конкретної операції; для URING_CMD не вживається */
    __u64  user_data;  /* Користувацький ідентифікатор запиту (повертається в CQE) */
    __u16  buf_index;  /* Індекс зареєстрованого буфера (при IORING_URING_CMD_FIXED) */
    __u16  personality;/* Контекст ідентичності (credentials) */
    union {
        __s32  splice_fd_in;
        __u32  file_index;
    };
    union {            /* усі варіанти починаються зі зсуву 48 байт */
        struct {
            __u64  addr3;
            __u64  __pad2[1];
        };
        __u8   cmd[0]; /* 16 байт у звичайному SQE, 80 байт при SQE128 */
    };
};
