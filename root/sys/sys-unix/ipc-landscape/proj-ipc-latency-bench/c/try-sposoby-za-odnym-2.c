static int open_pipe_pair(struct duplex *a, struct duplex *b, size_t n)
{
        int ab[2], ba[2];                       /* ab: A→B, ba: B→A */
        if (pipe(ab) != 0 || pipe(ba) != 0)
                return -1;
        /* Ємність каналу за замовчуванням — 16 сторінок, тобто 65536 Б
           (так від Linux 2.6.11).  Повідомлення більше за неї передається
           шматками, і КОЖЕН шматок — це засинання записувача.  Стеля
           прохання: /proc/sys/fs/pipe-max-size. */
        if (n > 65536) {
                fcntl(ab[1], F_SETPIPE_SZ, (int)n);
                fcntl(ba[1], F_SETPIPE_SZ, (int)n);
        }
        a->tx = ab[1]; a->rx = ba[0];
        b->tx = ba[1]; b->rx = ab[0];
        return 0;
}

static int open_socket_pair(struct duplex *a, struct duplex *b, size_t n)
{
        int s[2], want = (int)n;
        if (socketpair(AF_UNIX, SOCK_SEQPACKET, 0, s) != 0)
                return -1;
        /* SEQPACKET зберігає межі повідомлення — отже, воно мусить УМІСТИТИСЯ
           в буфер відправника цілком, інакше send дає EMSGSIZE.  Ядро вважає
           стелею подвоєне прохане мінус 32 Б, тож просимо рівно n — це вдвічі
           з запасом.  Саме прохання обмежене sysctl net.core.wmem_max, і на
           мегабайтовому повідомленні його доводиться піднімати.
           SO_RCVBUF для AF_UNIX не робить нічого — обмежує лише відправник. */
        for (int i = 0; i < 2; i++)
                if (setsockopt(s[i], SOL_SOCKET, SO_SNDBUF, &want, sizeof want) != 0)
                        perror("SO_SNDBUF");
        a->tx = a->rx = s[0];
        b->tx = b->rx = s[1];
        return 0;
}
