static void on_signal(int sig) { (void)sig; stopping = 1; }

int main(int argc, char **argv)
{
        struct io_uring_params cp = { .flags = IORING_SETUP_SQE128 };
        struct sigaction sa = { .sa_handler = on_signal };  /* без SA_RESTART: */
        struct stat st;                                     /* щоб очікування урвалося */
        unsigned t;
        int ret;

        if (argc != 2)
                return fprintf(stderr, "вжиток: %s <файл-підкладка>\n", argv[0]), 2;

        /* O_DIRECT: наші читання й записи не залежать від кешу сторінок */
        backing_fd = open(argv[1], O_RDWR | O_DIRECT);
        if (backing_fd < 0 || fstat(backing_fd, &st) < 0)
                return perror("підкладка"), 1;
        if ((ctrl_fd = open("/dev/ublk-control", O_RDWR)) < 0)
                return perror("/dev/ublk-control"), 1;
        io_uring_queue_init_params(32, &ctrl_ring, &cp);

        if ((ret = setup_device(st.st_size)) < 0)
                return fprintf(stderr, "створення: %s\n", strerror(-ret)), 1;
        if ((ret = open_channel()) < 0) {
                fprintf(stderr, "канал: %s\n", strerror(-ret));
                goto del;
        }

        for (t = 0; t < QDEPTH; t++)
                arm(t, UBLK_U_IO_FETCH_REQ, 0);
        io_uring_submit(&io_ring);              /* усі теги озброєні */

        sigaction(SIGINT, &sa, NULL);
        sigaction(SIGTERM, &sa, NULL);

        if ((ret = ctrl_cmd(UBLK_U_CMD_START_DEV, NULL, 0, (__u64)getpid())) < 0) {
                fprintf(stderr, "запуск: %s\n", strerror(-ret));
                goto del;
        }
        printf("/dev/ublkb%u живий; Ctrl-C — зупинити\n", info.dev_id);

        while (!stopping) {
                struct io_uring_cqe *cqe;
                unsigned tag;
                int res;

                if (io_uring_wait_cqe(&io_ring, &cqe) < 0)
                        break;                  /* сигнал урвав очікування */
                tag = (unsigned)io_uring_cqe_get_data64(cqe);
                res = cqe->res;
                io_uring_cqe_seen(&io_ring, cqe);

                if (res < 0)                    /* −ENODEV: пристрій зупиняють */
                        break;

                arm(tag, UBLK_U_IO_COMMIT_AND_FETCH_REQ, serve(&desc[tag], buf[tag]));
                io_uring_submit(&io_ring);
        }

        ctrl_cmd(UBLK_U_CMD_STOP_DEV, NULL, 0, 0);   /* блоковий вузол зникає */
del:
        ctrl_cmd(UBLK_U_CMD_DEL_DEV, NULL, 0, 0);    /* номер вивільняється */
        return 0;
}
