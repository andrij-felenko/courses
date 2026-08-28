int main(void)
{
    ring_setup();

    int lfd = socket(AF_INET, SOCK_STREAM, 0), one = 1;
    setsockopt(lfd, SOL_SOCKET, SO_REUSEADDR, &one, sizeof one);
    struct sockaddr_in a = { .sin_family = AF_INET, .sin_port = htons(PORT),
                             .sin_addr  = { htonl(INADDR_ANY) } };
    if (bind(lfd, (struct sockaddr *)&a, sizeof a) || listen(lfd, 512))
        { perror("bind/listen"); return 1; }

    arm_accept(lfd);

    for (;;) {
        int ret = io_uring_submit_and_wait(&ring, 1);   /* один перехід межі на прохід */
        if (ret < 0 && ret != -EINTR)
            { fprintf(stderr, "submit: %s\n", strerror(-ret)); return 1; }

        unsigned head, seen = 0;
        struct io_uring_cqe *cqe;

        io_uring_for_each_cqe(&ring, head, cqe) {
            __u64 u  = cqe->user_data;
            int   fd = UD_FD(u);
            seen++;

            switch (UD_OP(u)) {
            case OP_ACCEPT:
                if (cqe->res >= 0 && cqe->res < MAX_CONN) {
                    conns[cqe->res] = (struct conn){ .bid = -1 };
                    arm_recv(cqe->res);
                } else if (cqe->res >= 0) {
                    close(cqe->res);                  /* дескриптор поза таблицею */
                }
                if (!(cqe->flags & IORING_CQE_F_MORE))
                    arm_accept(fd);                   /* багаторазовий accept помер */
                break;

            case OP_RECV:
                if (cqe->res == -ENOBUFS) {           /* вільних буферів немає */
                    starved[n_starved++] = fd;        /* чекаємо на чужий повернений */
                    break;
                }
                if (cqe->res <= 0) {                  /* 0 — інший бік закрив */
                    if (cqe->flags & IORING_CQE_F_BUFFER)
                        buf_give_back(cqe->flags >> IORING_CQE_BUFFER_SHIFT);
                    close(fd);
                    break;
                }
                conns[fd] = (struct conn){
                    .bid  = cqe->flags >> IORING_CQE_BUFFER_SHIFT,
                    .off  = 0,
                    .left = (unsigned)cqe->res,
                };
                arm_send(fd);
                break;

            case OP_SEND: {
                struct conn *c = &conns[fd];
                if (cqe->res <= 0) {                  /* з'єднання обірвалося */
                    buf_give_back(c->bid);
                    close(fd);
                    break;
                }
                c->off  += (unsigned)cqe->res;
                c->left -= (unsigned)cqe->res;
                if (c->left) { arm_send(fd); break; } /* частковий запис */

                buf_give_back(c->bid);                /* аж тепер буфер вільний */
                c->bid = -1;
                arm_recv(fd);
                break;
            }
            }
        }
        io_uring_cq_advance(&ring, seen);
    }
}
