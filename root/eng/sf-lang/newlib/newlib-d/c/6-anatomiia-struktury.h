struct __sFILE {
    unsigned char *_p;   /* Поточний покажчик у буфері I/O */
    int            _r;   /* Кількість байтів, доступних для читання */
    int            _w;   /* Кількість вільного місця для запису */
    short          _flags;/* Прапорці стану: читання, запис, помилка, EOF */
    short          _file; /* Номер файлового дескриптора (fd) */
    struct __sbuf  _bf;  /* Опис буфера: адреса початку та загальний розмір */
    int            _lbfsize; /* Розмір буфера рядка */
    
    /* Функціональні покажчики (Cookie I/O) */
    void          *_cookie;
    _READ_WRITE_RETURN_TYPE (*_read) (struct _reent *, void *, char *, int);
    _READ_WRITE_RETURN_TYPE (*_write)(struct _reent *, void *, const char *, int);
    _fpos_t                 (*_seek) (struct _reent *, void *, _fpos_t, int);
    int                     (*_close)(struct _reent *, void *);
};
