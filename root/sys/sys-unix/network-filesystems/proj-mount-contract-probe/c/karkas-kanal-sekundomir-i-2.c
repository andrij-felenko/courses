#define SLOTS 4
static int slot[SLOTS];

static void ok(long v)  { char b[64]; snprintf(b, sizeof b, "OK %ld",  v);     send_line(b); }
static void err(void)   { char b[64]; snprintf(b, sizeof b, "ERR %d", errno);  send_line(b); }
static int  sl(long i)  { return (i >= 0 && i < SLOTS) ? slot[i] : -1; }

static int mode_flags(const char *m)
{
    if (!strcmp(m, "r"))  return O_RDONLY;
    if (!strcmp(m, "rw")) return O_RDWR   | O_CREAT;
    if (!strcmp(m, "w"))  return O_WRONLY | O_CREAT | O_TRUNC;
    if (!strcmp(m, "wx")) return O_WRONLY | O_CREAT | O_EXCL;
    return -1;
}

static long count_prefix(const char *dir, const char *prefix)
{
    DIR           *d = opendir(dir);
    struct dirent *e;
    size_t         plen = strlen(prefix);
    long           k = 0;

    if (!d) return -1;
    while ((e = readdir(d)) != NULL)
        if (strncmp(e->d_name, prefix, plen) == 0) k++;
    closedir(d);
    return k;
}

static void race(const char *prefix, int rounds, char *bits)
{
    int i;
    for (i = 0; i < rounds; i++) {
        char name[600];
        int  fd;
        snprintf(name, sizeof name, "%s-%d", prefix, i);
        fd = open(at(name), O_WRONLY | O_CREAT | O_EXCL, 0644);
        if (fd >= 0) { bits[i] = '1'; close(fd); }
        else           bits[i] = '0';
    }
    bits[rounds] = '\0';
}

static void serve(void)
{
    char cmd[2048], a[64], b[512];
    long i, n, off;

    for (i = 0; i < SLOTS; i++) slot[i] = -1;

    while (recv_line(cmd, sizeof cmd) == 0) {

        if (sscanf(cmd, "OPEN %ld %63s %511s", &i, a, b) == 3
            && i >= 0 && i < SLOTS) {
            int fl = mode_flags(a);
            slot[i] = (fl < 0) ? -1 : open(at(b), fl, 0644);
            if (slot[i] < 0) err(); else ok(0);
        }
        else if (sscanf(cmd, "WRITE %ld %ld", &i, &n) == 2) {
            char   *buf = malloc((size_t) n);
            ssize_t w = -1;
            if (buf) { memset(buf, 'x', (size_t) n); w = write(sl(i), buf, (size_t) n); }
            free(buf);
            if (w != (ssize_t) n) err(); else ok(n);
        }
        else if (sscanf(cmd, "FSYNC %ld", &i) == 1) {
            if (fsync(sl(i)) < 0) err(); else ok(0);
        }
        else if (sscanf(cmd, "PREAD %ld %ld %ld", &i, &off, &n) == 3) {
            char    buf[4096];
            ssize_t r;
            if (n > (long) sizeof buf) n = (long) sizeof buf;
            r = pread(sl(i), buf, (size_t) n, (off_t) off);
            if (r < 0) err(); else ok(r);
        }
        else if (sscanf(cmd, "CLOSE %ld", &i) == 1) {
            int rc = close(sl(i));              /* саме тут NFS віддає накопичене */
            if (i >= 0 && i < SLOTS) slot[i] = -1;
            if (rc < 0) err(); else ok(0);
        }
        else if (sscanf(cmd, "FLOCK %ld", &i) == 1) {
            if (flock(sl(i), LOCK_EX | LOCK_NB) < 0) err(); else ok(0);
        }
        else if (sscanf(cmd, "FCNTL %ld", &i) == 1) {
            struct flock fl;
            memset(&fl, 0, sizeof fl);          /* l_start = 0, l_len = 0 — увесь файл */
            fl.l_type = F_WRLCK;
            fl.l_whence = SEEK_SET;
            if (fcntl(sl(i), F_SETLK, &fl) < 0) err(); else ok(0);
        }
        else if (sscanf(cmd, "UNLINK %511s", b) == 1) {
            if (unlink(at(b)) < 0) err(); else ok(0);
        }
        else if (sscanf(cmd, "COUNT %511s", b) == 1) {
            ok(count_prefix(share, b));
        }
        else if (sscanf(cmd, "RACE %511s %ld", b, &n) == 2) {
            char *bits = malloc((size_t) n + 1);
            if (!bits) { err(); continue; }
            race(b, (int) n, bits);
            send_line(bits);                    /* відповідь — мапа, а не OK */
            free(bits);
        }
        else if (!strcmp(cmd, "BYE")) return;
        else send_line("ERR 22");               /* EINVAL: незрозуміла команда */
    }
}
