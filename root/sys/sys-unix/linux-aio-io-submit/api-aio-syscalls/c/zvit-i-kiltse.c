struct io_event {
    __u64 data;   /* мітка з aio_data */
    __u64 obj;    /* адреса поданого iocb */
    __s64 res;    /* передані байти або від'ємний код помилки */
    __s64 res2;   /* другорядний результат; на всіх сучасних шляхах нуль */
};

#define AIO_RING_MAGIC             0xa10a10a1
#define AIO_RING_COMPAT_FEATURES   1
#define AIO_RING_INCOMPAT_FEATURES 0

struct aio_ring {
    unsigned id, nr, head, tail;
    unsigned magic, compat_features, incompat_features, header_length;
    struct io_event io_events[];
};
