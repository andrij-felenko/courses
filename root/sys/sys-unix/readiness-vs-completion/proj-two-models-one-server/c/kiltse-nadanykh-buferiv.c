#define NBUF   2048
#define BUFSZ  (16 * 1024)
#define BGID   7

static struct io_uring_buf_ring *br;
static uint8_t *pool;
static int      br_mask;

static int setup_bufs(struct io_uring *r) {
    int err;
    br = io_uring_setup_buf_ring(r, NBUF, BGID, 0, &err);   /* NBUF — степінь двійки */
    if (!br) { errno = -err; return -1; }
    br_mask = io_uring_buf_ring_mask(NBUF);
    pool = malloc((size_t)NBUF * BUFSZ);
    for (int i = 0; i < NBUF; i++)
        io_uring_buf_ring_add(br, pool + (size_t)i * BUFSZ, BUFSZ, i, br_mask, i);
    io_uring_buf_ring_advance(br, NBUF);                    /* тепер їх бачить ядро */
    return 0;
}

static void arm_recv(struct io_uring *r, struct uconn *u) {
    if (u->closing) return;
    struct io_uring_sqe *sqe = io_uring_get_sqe(r);
    io_uring_prep_recv(sqe, u->c.fd, NULL, 0, 0);           /* адреси немає — обере ядро */
    sqe->flags     |= IOSQE_BUFFER_SELECT;
    sqe->buf_group  = BGID;
    io_uring_sqe_set_data64(sqe, TAG(u, OP_RECV));
    u->refs++;
}
