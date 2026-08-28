struct aiocb {
    int             aio_fildes;     /* дескриптор */
    off_t           aio_offset;     /* абсолютне зміщення у файлі */
    volatile void  *aio_buf;        /* буфер */
    size_t          aio_nbytes;     /* скільки байтів */
    int             aio_reqprio;    /* наскільки ЗНИЗИТИ пріоритет запиту */
    struct sigevent aio_sigevent;   /* як сповістити про завершення */
    int             aio_lio_opcode; /* LIO_READ / LIO_WRITE / LIO_NOP */
    /* далі — внутрішні поля реалізації */
};
