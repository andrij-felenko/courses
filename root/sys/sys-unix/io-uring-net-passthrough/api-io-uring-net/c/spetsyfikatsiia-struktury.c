/* c */
struct io_uring_sqe {
    __u8   opcode;      /* IORING_OP_SEND_ZC */
    __u8   flags;       /* IOSQE_FIXED_FILE, IOSQE_CQE_SKIP_SUCCESS тощо */
    __u16  ioprio;      /* Прапорці відправки: IORING_RECVSEND_FIXED_BUF тощо */
    __s32  fd;          /* Мережевий файловий дескриптор (сокет) */
    __u64  off;         /* Не використовується або розширений зміщення */
    __u64  addr;        /* Вказівник на буфер користувача (char*) або offset */
    __u32  len;         /* Довжина буфера в байтах */
    __u32  msg_flags;   /* Мережеві прапорці сокета (наприклад, MSG_DONTWAIT) */
    __u64  user_data;   /* Ідентифікатор запиту користувача */
    __u16  buf_index;   /* Індекс зареєстрованого буфера (якщо в іоprio є FIXED_BUF) */
    __u16  personality; /* Права доступу / credentials */
    __u32  file_index;  /* Індекс у таблиці зареєстрованих файлів */
    __u64  addr3;       /* Прапорці нотифікації або розширені параметри */
};
