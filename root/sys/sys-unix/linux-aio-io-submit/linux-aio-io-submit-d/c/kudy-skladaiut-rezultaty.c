struct aio_ring {
    unsigned  id;
    unsigned  nr;                /* скільки комірок */
    unsigned  head;             /* звідки читає програма */
    unsigned  tail;             /* куди пише ядро */
    unsigned  magic;            /* 0xa10a10a1 */
    unsigned  compat_features;
    unsigned  incompat_features;
    unsigned  header_length;
    struct io_event io_events[];
};
