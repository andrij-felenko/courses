case OP_RECV:
    u->refs--;
    if (cqe->res == -ENOBUFS) { stall(u); break; }   /* пул порожній: тиснемо назад */
    if (cqe->res <= 0)        { begin_close(&ring, u); break; }

    int bid = cqe->flags >> IORING_CQE_BUFFER_SHIFT;
    uint8_t *data = pool + (size_t)bid * BUFSZ;
    int rc = feed(&u->c, data, (size_t)cqe->res);

    io_uring_buf_ring_add(br, data, BUFSZ, bid, br_mask, 0);  /* ПОВЕРНУТИ — завжди, */
    io_uring_buf_ring_advance(br, 1);                         /* і на шляху помилки теж */

    if (rc < 0) { begin_close(&ring, u); break; }
    ...
