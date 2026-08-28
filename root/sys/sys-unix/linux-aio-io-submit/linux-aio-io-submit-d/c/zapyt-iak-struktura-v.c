struct iocb {
    __u64  aio_data;        /* мітка: ядро поверне її незміненою */
    __u32  PADDED(aio_key, aio_rw_flags);
    __u16  aio_lio_opcode;  /* IOCB_CMD_PREAD, PWRITE, FSYNC, POLL… */
    __s16  aio_reqprio;
    __u32  aio_fildes;      /* дескриптор */
    __u64  aio_buf;         /* адреса буфера */
    __u64  aio_nbytes;      /* скільки байтів */
    __s64  aio_offset;      /* з якого зміщення у файлі */
    __u64  aio_reserved2;
    __u32  aio_flags;       /* IOCB_FLAG_RESFD, IOCB_FLAG_IOPRIO */
    __u32  aio_resfd;       /* eventfd, який смикнути на завершення */
};
