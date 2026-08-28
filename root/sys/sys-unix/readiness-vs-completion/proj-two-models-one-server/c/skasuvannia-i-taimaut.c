static void arm_recv_timed(struct io_uring *r, struct uconn *u, time_t sec) {
    struct io_uring_sqe *sqe = io_uring_get_sqe(r);
    io_uring_prep_recv(sqe, u->c.fd, u->in, sizeof u->in, 0);
    io_uring_sqe_set_data64(sqe, TAG(u, OP_RECV));
    sqe->flags |= IOSQE_IO_LINK;              /* наступний SQE — таймер ЦЬОГО читання */
    u->refs++;

    u->ts = (struct __kernel_timespec){ .tv_sec = sec };   /* поле з'єднання, не стек! */
    sqe = io_uring_get_sqe(r);
    io_uring_prep_link_timeout(sqe, &u->ts, 0);
    io_uring_sqe_set_data64(sqe, TAG(u, OP_TMO));
    u->refs++;
}
