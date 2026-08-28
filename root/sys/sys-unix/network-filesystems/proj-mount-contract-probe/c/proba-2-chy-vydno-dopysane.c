static void probe_open_file(void)
{
    char        name[64], path[PATH_MAX];
    struct stat st;
    off_t       base;
    double      t0, tsize = -1, tdata = -1, treopen = -1;
    int         fd;

    snprintf(name, sizeof name, "app-%ld", (long) getpid());
    snprintf(path, sizeof path, "%s/%s", share, name);

    rpc("UNLINK %s", name);                       /* байдуже, чи був */
    if (rpc("OPEN 0 w %s", name) < 0) { puts("2. створити не вдалося"); return; }
    rpc("WRITE 0 4096");
    rpc("FSYNC 0");

    fd = open(path, O_RDONLY);                    /* відкриваємо ПІСЛЯ — CTO має діяти */
    if (fd < 0) { perror("2. open"); return; }
    if (fstat(fd, &st) < 0) { close(fd); return; }
    base = st.st_size;

    rpc("WRITE 0 4096");                          /* дописано, файл лишається відкритим */
    rpc("FSYNC 0");
    t0 = mono();

    while (mono() - t0 < 180.0 && (tsize < 0 || tdata < 0 || treopen < 0)) {
        char c;
        int  g;
        if (tsize < 0 && fstat(fd, &st) == 0 && st.st_size > base)
            tsize = mono() - t0;
        if (tdata < 0 && pread(fd, &c, 1, base) == 1)
            tdata = mono() - t0;
        if (treopen < 0 && (g = open(path, O_RDONLY)) >= 0) {
            if (pread(g, &c, 1, base) == 1) treopen = mono() - t0;
            close(g);
        }
        nap_ms(50);
    }

    printf("2a. новий розмір видно через         %s с\n", secs(tsize));
    printf("2b. дописані байти читаються через   %s с\n", secs(tdata));
    printf("2c. те саме з перевідкриттям файлу:  %s с\n", secs(treopen));

    close(fd);
    rpc("CLOSE 0");
    rpc("UNLINK %s", name);
}
