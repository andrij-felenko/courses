static void consumer(int sock)
{
    const int need = F_SEAL_SHRINK | F_SEAL_WRITE;

    int fd = recv_fd(sock);
    if (fd < 0) die("recv_fd");

    int seals = fcntl(fd, F_GET_SEALS);            /* ПЕРЕД усім іншим */
    if (seals < 0) {                               /* EINVAL: файл без пломб */
        printf("[споживач] F_GET_SEALS → %s — це не memfd\n", strerror(errno));
        _exit(1);
    }
    printf("[споживач] пломби 0x%x%s\n", seals,
           (seals & need) == need ? " — усе на місці" : " — БРАКУЄ потрібних");

    if (fcntl(fd, F_ADD_SEALS, F_SEAL_FUTURE_WRITE) < 0)
        printf("[споживач] моя спроба допломбувати → %s\n", strerror(errno));

    struct stat st;
    if (fstat(fd, &st) < 0) die("fstat");          /* лише тепер розмір — факт */
    size_t bytes = (size_t)st.st_size;

    const struct frame *f = mmap(NULL, bytes, PROT_READ, MAP_SHARED, fd, 0);
    if (f == MAP_FAILED && errno == EPERM)         /* ядра до 6.7 */
        f = mmap(NULL, bytes, PROT_READ, MAP_PRIVATE, fd, 0);
    if (f == MAP_FAILED) die("mmap");

    uint32_t w = f->w, h = f->h;
    printf("[споживач] кадр %ux%u, перший піксель 0x%08x\n", w, h, f->px[0]);

    char t;
    if (write(sock, "A", 1) != 1) die("write");
    if (read(sock, &t, 1) != 1) die("read");       /* сусід уже спробував різати */

    puts("[споживач] торкаюся останнього пікселя...");
    printf("[споживач] останній піксель 0x%08x\n", f->px[(size_t)w * h - 1]);
    munmap((void *)f, bytes);
    close(fd);
}
