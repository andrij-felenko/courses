for (;;) {
    io_uring_submit_and_wait(&ring, 1);
    unsigned head, count = 0;
    struct io_uring_cqe *cqe;

    io_uring_for_each_cqe(&ring, head, cqe) {
        count++;
        struct uconn *u = PTR(cqe->user_data);
        switch (OPC(cqe->user_data)) {

        case OP_RECV:
            u->refs--;
            if (cqe->res <= 0) {                       /* 0 — закриття, <0 — це −errno */
                begin_close(&ring, u);                 /* ECONNRESET приїде як −104 */
                break;
            }
            if (feed(&u->c, u->in, (size_t)cqe->res) < 0) { begin_close(&ring, u); break; }
            if (u->c.out_len > u->c.out_sent) arm_send(&ring, u);
            else                              arm_recv(&ring, u);
            break;

        case OP_SEND:
            u->refs--;
            if (cqe->res < 0) { begin_close(&ring, u); break; }
            u->c.out_sent += (size_t)cqe->res;         /* часткова передача */
            if (u->c.out_sent < u->c.out_len) { arm_send(&ring, u); break; } /* ЗАЛИШОК */
            u->c.out_len = u->c.out_sent = 0;
            arm_recv(&ring, u);
            break;

        case OP_CANCEL: case OP_TMO:
            u->refs--;               /* −ENOENT тут нормальне: скасовувати не було чого */
            break;
        }
        if (u->refs == 0 && u->closing) reap(u);       /* єдине місце, де є free() */
    }
    io_uring_cq_advance(&ring, count);
}
