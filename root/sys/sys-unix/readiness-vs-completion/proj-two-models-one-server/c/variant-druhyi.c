struct uconn {
    struct conn  c;
    uint8_t      in[16 * 1024];   /* буфер ЦЬОГО з'єднання під подане читання */
    unsigned     refs;            /* операцій у польоті */
    int          closing;
    struct __kernel_timespec ts;  /* мусить пережити свою операцію */
};

static void arm_recv(struct io_uring *r, struct uconn *u) {
    if (u->closing) return;
    struct io_uring_sqe *sqe = io_uring_get_sqe(r);
    io_uring_prep_recv(sqe, u->c.fd, u->in, sizeof u->in, 0);
    io_uring_sqe_set_data64(sqe, TAG(u, OP_RECV));
    u->refs++;                    /* з цієї миті u->in і u->c.fd належать ядру */
}

static void arm_send(struct io_uring *r, struct uconn *u) {
    struct io_uring_sqe *sqe = io_uring_get_sqe(r);
    io_uring_prep_send(sqe, u->c.fd, u->c.out + u->c.out_sent,
                       u->c.out_len - u->c.out_sent, MSG_NOSIGNAL);
    io_uring_sqe_set_data64(sqe, TAG(u, OP_SEND));
    u->refs++;
}
