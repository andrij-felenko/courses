static int do_send(void)
{
    int buf = heap_alloc(BYTES);

    off_t size = lseek(buf, 0, SEEK_END);   /* єдине, що дескриптор розповідає про себе */
    if (size < 0) die("lseek");

    void *p = mmap(NULL, size, PROT_READ | PROT_WRITE, MAP_SHARED, buf, 0);
    if (p == MAP_FAILED) die("mmap");

    struct handoff h = { .bytes = BYTES, .seed = (uint32_t)getpid() };
    uint32_t *w = p;
    size_t words = BYTES / 4;

    sync_start(buf, DMA_BUF_SYNC_WRITE);
    for (size_t i = 0; i < words; i++) w[i] = word_at(h.seed, i);
    sync_end(buf, DMA_BUF_SYNC_WRITE);

    int sock = socket(AF_UNIX, SOCK_STREAM | SOCK_CLOEXEC, 0);
    if (sock < 0) die("socket");
    struct sockaddr_un a; socklen_t alen; addr_init(&a, &alen);
    for (int t = 0; connect(sock, (struct sockaddr *)&a, alen) < 0; t++) {
        if (t == 50 || errno != ECONNREFUSED) die("connect");
        usleep(20000);                      /* приймач ще не став на адресу */
    }
    send_fd(sock, buf, &h);

    char ok;
    if (read(sock, &ok, 1) != 1) { fputs("приймач мовчить\n", stderr); exit(1); }

    sync_start(buf, DMA_BUF_SYNC_READ);
    uint32_t mark = w[words - 1];
    sync_end(buf, DMA_BUF_SYNC_READ);

    printf("А: останнє слово тепер 0x%08x, а клав 0x%08x\n",
           mark, word_at(h.seed, words - 1));

    munmap(p, size);
    close(buf);                             /* наше посилання пішло */
    close(sock);
    return 0;
}

static int do_recv(void)
{
    int srv = socket(AF_UNIX, SOCK_STREAM | SOCK_CLOEXEC, 0);
    if (srv < 0) die("socket");
    struct sockaddr_un a; socklen_t alen; addr_init(&a, &alen);
    if (bind(srv, (struct sockaddr *)&a, alen) < 0) die("bind");
    if (listen(srv, 1) < 0) die("listen");

    int sock = accept(srv, NULL, NULL);
    if (sock < 0) die("accept");

    struct handoff h;
    int buf = recv_fd(sock, &h);

    off_t size = lseek(buf, 0, SEEK_END);
    if (size < 0) die("lseek");
    if (h.bytes > (uint64_t)size) { fputs("заголовок бреше про довжину\n", stderr); exit(1); }

    void *p = mmap(NULL, size, PROT_READ | PROT_WRITE, MAP_SHARED, buf, 0);
    if (p == MAP_FAILED) die("mmap");

    uint32_t *w = p;
    size_t words = h.bytes / 4, bad = 0;

    sync_start(buf, DMA_BUF_SYNC_READ);
    for (size_t i = 0; i < words; i++) if (w[i] != word_at(h.seed, i)) bad++;
    sync_end(buf, DMA_BUF_SYNC_READ);

    printf("Б: буфер %lld Б, звірено %zu слів, розбіжностей %zu\n",
           (long long)size, words, bad);

    sync_start(buf, DMA_BUF_SYNC_WRITE);
    w[words - 1] = 0xb0b0b0b0u;             /* позначка, яку має побачити А */
    sync_end(buf, DMA_BUF_SYNC_WRITE);

    if (write(sock, "1", 1) != 1) die("write");

    munmap(p, size);
    close(buf);
    close(sock);
    close(srv);
    return 0;
}

int main(int argc, char **argv)
{
    if (argc == 2 && !strcmp(argv[1], "send")) return do_send();
    if (argc == 2 && !strcmp(argv[1], "recv")) return do_recv();
    fprintf(stderr, "вжиток: %s send|recv\n", argv[0]);
    return 2;
}
