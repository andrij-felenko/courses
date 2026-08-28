static void run_client(const char *host, int port, int nodelay, int iters)
{
    int fd = socket(AF_INET, SOCK_STREAM, 0);
    struct sockaddr_in a = { .sin_family = AF_INET,
                             .sin_port = htons((uint16_t)port) };
    if (inet_pton(AF_INET, host, &a.sin_addr) != 1) { fprintf(stderr, "адреса?\n"); return; }
    if (connect(fd, (struct sockaddr *)&a, sizeof a) < 0) { perror("connect"); return; }

    /* ЄДИНА відмінність між двома прогонами. Ставимо після connect свідомо:
       притримування — властивість машини TCP, а не рукостискання, тож для
       цієї опції момент не важить. Для розмірів буферів було б уже пізно. */
    if (nodelay) {
        int on = 1;
        if (setsockopt(fd, IPPROTO_TCP, TCP_NODELAY, &on, sizeof on) < 0)
            perror("TCP_NODELAY");
    }

    unsigned char hdr[HDR] = {0}, body[BODY] = {0}, back[HDR];
    double *ms = malloc(sizeof *ms * (size_t)iters);
    if (!ms) return;
    int n = 0;

    for (int i = 0; i < iters + WARMUP; i++) {
        double t0 = now_us();

        /* Візерунок, заради якого все це: ДВА записи, тоді читання. */
        if (send(fd, hdr,  HDR,  0) != (ssize_t)HDR)  break;
        if (send(fd, body, BODY, 0) != (ssize_t)BODY) break;
        if (read_exact(fd, back, HDR) < 0)            break;

        double dt = now_us() - t0;
        if (i >= WARMUP) ms[n++] = dt / 1000.0;
    }
    close(fd);

    if (n > 0) histogram(ms, n);
    free(ms);
}
