static volatile sig_atomic_t watching;
static int peak;

static int threads_now(void)
{
    int n = 0;
    char line[128];
    FILE *f = fopen("/proc/self/status", "r");
    if (!f) return 0;
    while (fgets(line, sizeof line, f))
        if (sscanf(line, "Threads: %d", &n) == 1) break;
    fclose(f);
    return n;
}

static void *watcher(void *arg)
{
    (void)arg;
    while (watching) {
        int t = threads_now();
        if (t > peak) peak = t;
        nanosleep(&(struct timespec){ 0, 200000 }, NULL);   /* 0.2 мс */
    }
    return NULL;
}

static void run(const char *path, int nfd)
{
    int fd[MAXFD];
    struct stat st;
    pthread_t w;
    struct timespec t0, t1;

    sleep(2);          /* дати вмерти робітникам минулого заміру:
                          aio_idle_time за замовчуванням — 1 секунда */

    for (int i = 0; i < nfd; i++)
        if ((fd[i] = open(path, O_RDONLY | O_DIRECT)) < 0)
            { perror("open O_DIRECT"); exit(1); }
    fstat(fd[0], &st);

    struct batch *b = batch_make(fd, nfd, NREQ, st.st_size / BLK);

    peak = 0;
    watching = 1;
    pthread_create(&w, NULL, watcher, NULL);
    int base = threads_now();          /* ми самі: головний потік і наглядач */

    clock_gettime(CLOCK_MONOTONIC, &t0);
    submit(b);
    size_t got = drain(b);
    clock_gettime(CLOCK_MONOTONIC, &t1);

    watching = 0;
    pthread_join(w, NULL);

    double ms = (t1.tv_sec - t0.tv_sec) * 1e3 + (t1.tv_nsec - t0.tv_nsec) / 1e6;
    printf("%3d дескрипторів  %3d робітників  %7.2f мс  %6.1f мкс/запит  %zu Б\n",
           nfd, peak - base, ms, ms * 1000 / NREQ, got);

    for (int i = 0; i < NREQ; i++) free(b->buf[i]);
    free(b->buf); free(b->cb); free(b);
    for (int i = 0; i < nfd; i++) close(fd[i]);   /* усі запити вже забрані */
}

int main(int argc, char **argv)
{
    const char *path = argc > 1 ? argv[1] : "/var/tmp/aio.bin";  /* ≥ 1 ГіБ, ext4 чи XFS */

    run(path,  1);      /* усі 256 запитів в одну чергу     */
    run(path, 16);      /* ті самі 256 — на 16 черг         */
    run(path, 32);      /* черг більше, ніж дозволяє пул    */
    return 0;
}
