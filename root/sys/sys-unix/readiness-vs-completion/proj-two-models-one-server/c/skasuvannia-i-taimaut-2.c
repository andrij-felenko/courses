static void begin_close(struct io_uring *r, struct uconn *u) {
    if (u->closing) return;
    u->closing = 1;
    struct io_uring_sqe *sqe = io_uring_get_sqe(r);
    io_uring_prep_cancel64(sqe, TAG(u, OP_RECV), 0);   /* у польоті або воно, або запис: */
    io_uring_sqe_set_data64(sqe, TAG(u, OP_CANCEL));   /* запис доживе сам і теж віддасть */
    u->refs++;                       /* сама відмова теж тримає з'єднання живим */
}

static void reap(struct uconn *u) {  /* викликається ЛИШЕ при refs == 0 */
    close(u->c.fd);
    free(u->c.out);
    free(u);
}
