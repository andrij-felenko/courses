static void probe_write_path(void)
{
    enum { CHUNKS = 64 };
    const size_t CHUNK = 1u << 20;                /* 1 МіБ */
    char   name[64], path[PATH_MAX], *buf;
    double t0, t_write, t_fsync, t_close;
    int    fd, i, rc = 0;

    buf = malloc(CHUNK);
    if (!buf) return;
    memset(buf, 'z', CHUNK);
    snprintf(name, sizeof name, "flush-%ld", (long) getpid());
    snprintf(path, sizeof path, "%s/%s", share, name);

    fd = open(path, O_WRONLY | O_CREAT | O_TRUNC, 0644);
    if (fd < 0) { perror("3. open"); free(buf); return; }

    t0 = mono();
    for (i = 0; i < CHUNKS; i++)
        if (write(fd, buf, CHUNK) != (ssize_t) CHUNK) { rc = -1; break; }
    t_write = mono() - t0;

    t0 = mono();
    if (fsync(fd) < 0) rc = -1;
    t_fsync = mono() - t0;

    t0 = mono();
    if (close(fd) < 0) rc = -1;                   /* ← результат close() перевіряємо ЗАВЖДИ */
    t_close = mono() - t0;

    printf("3.  %d МіБ:  write() %.2f с   fsync() %.2f с   close() %.2f с%s\n",
           (int) CHUNKS, t_write, t_fsync, t_close, rc < 0 ? "   ← ПОМИЛКА" : "");
    printf("    сукупний темп ≈ %.0f МіБ/с\n",
           CHUNKS / (t_write + t_fsync + t_close + 1e-9));

    free(buf);
    unlink(path);
}
