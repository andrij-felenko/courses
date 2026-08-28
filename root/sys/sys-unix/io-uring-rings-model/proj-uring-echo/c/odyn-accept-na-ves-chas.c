static struct io_uring_sqe *sqe_get(void)
{
    struct io_uring_sqe *sqe = io_uring_get_sqe(&ring);
    if (!sqe) {                       /* кільце подань заповнене */
        io_uring_submit(&ring);       /* єдиний спосіб звільнити місце */
        sqe = io_uring_get_sqe(&ring);
        if (!sqe) { fprintf(stderr, "SQ не звільнилася\n"); exit(1); }
    }
    return sqe;
}

static void arm_accept(int lfd)
{
    struct io_uring_sqe *sqe = sqe_get();
    io_uring_prep_multishot_accept(sqe, lfd, NULL, NULL, 0);
    io_uring_sqe_set_data64(sqe, UD(OP_ACCEPT, lfd));
}

static void arm_recv(int fd)
{
    struct io_uring_sqe *sqe = sqe_get();
    io_uring_prep_recv(sqe, fd, NULL, BUF_SIZE, 0);   /* буфер обере ядро */
    io_uring_sqe_set_flags(sqe, IOSQE_BUFFER_SELECT);
    sqe->buf_group = BGID;
    io_uring_sqe_set_data64(sqe, UD(OP_RECV, fd));
}

static void arm_send(int fd)
{
    struct conn *c = &conns[fd];
    struct io_uring_sqe *sqe = sqe_get();
    io_uring_prep_send(sqe, fd, buf_at(c->bid) + c->off, c->left,
                       MSG_WAITALL | MSG_NOSIGNAL);
    io_uring_sqe_set_data64(sqe, UD(OP_SEND, fd));
}

static void buf_give_back(int bid)
{
    io_uring_buf_ring_add(br, buf_at(bid), BUF_SIZE, bid,
                          io_uring_buf_ring_mask(BUF_COUNT), 0);
    io_uring_buf_ring_advance(br, 1);
    if (n_starved)                    /* буфер звільнився — розбудити чекальника */
        arm_recv(starved[--n_starved]);
}
