struct io_uring_sqe {
    __u8    opcode;       /* Код операції (IORING_OP_*) */
    __u8    flags;        /* Прапорці поведінки запиту (IOSQE_*) */
    __u16   ioprio;       /* Пріоритет I/O (IOPRIO_CLASS_*) */
    __s32   fd;           /* Файловий дескриптор або індекс у масиві */
    union {
        __u64   off;      /* Зміщення у файлі */
        __u64   addr2;    /* Друга адреса для операцій splice/cmd */
    };
    union {
        __u64   addr;     /* Вказівник на буфер користувача або iovec */
        __u64   splice_off_in;
    };
    __u32   len;          /* Довжина буфера або кількість iovec */
    union {
        __kernel_rwf_t  rw_flags; /* Прапорці read/write (RWF_HIPRI, RWF_NOWAIT) */
        __u32           fsync_flags;
        __u16           poll_events;
        __u32           sync_range_flags;
        __u32           msg_flags;
        __u32           timeout_flags;
        __u32           accept_flags;
        __u32           cancel_flags;
        __u32           open_flags;
        __u32           statx_flags;
        __u32           fadvise_advise;
        __u32           splice_flags;
        __u32           rename_flags;
        __u32           unlink_flags;
        __u32           hardlink_flags;
        __u32           xattr_flags;
        __u32           msg_ring_flags;
        __u32           uring_cmd_flags;
    };
    __u64   user_data;    /* 64-бітне значення для ідентифікації запиту розробником */
    union {
        __u16   buf_index;  /* Індекс у масиві зареєстрованих буферів */
        __u16   buf_group;  /* Група наданих буферів (provided buffers) */
    } __attribute__((packed));
    __u16   personality;  /* Ідентифікатор прав (credentials) */
    union {
        __s32   splice_fd_in;
        __u32   file_index; /* Індекс для прямого файлового дескриптора */
    };
    __u64   __pad2[2];    /* Резерв для майбутніх розширень */
};
