/* Зсув у файлі → фізичний зсув на блоковому пристрої. Відповідає файлова
   система: вона одна знає, якими екстентами розкладено файл. */
static int file_off_to_phys(int fd, off_t off, uint64_t *phys)
{
    struct { struct fiemap m; struct fiemap_extent e; } q;

    memset(&q, 0, sizeof q);
    q.m.fm_start        = (uint64_t)off;
    q.m.fm_length       = 4096;
    q.m.fm_flags        = FIEMAP_FLAG_SYNC;  /* спершу висадити на носій */
    q.m.fm_extent_count = 1;

    if (ioctl(fd, FS_IOC_FIEMAP, &q.m) < 0) return -1;
    if (q.m.fm_mapped_extents != 1) { errno = ENOENT; return -1; }  /* діра */

    *phys = q.e.fe_physical + ((uint64_t)off - q.e.fe_logical);
    return 0;
}

/* Де шукати список і на скільки секторів зсунуто розділ від початку пристрою.
   Файл «start» є лише в розділу; список badblocks — завжди в цілого. */
static int find_device(int fd, char *bb, size_t sz, unsigned long long *part)
{
    struct stat st;
    char dir[96], p[160], buf[64];
    int f;

    if (fstat(fd, &st) < 0) return -1;
    snprintf(dir, sizeof dir, "/sys/dev/block/%u:%u",
             major(st.st_dev), minor(st.st_dev));

    *part = 0;
    snprintf(p, sizeof p, "%s/start", dir);
    f = open(p, O_RDONLY);
    if (f >= 0) {
        ssize_t k = read(f, buf, sizeof buf - 1);
        close(f);
        if (k > 0) { buf[k] = '\0'; *part = strtoull(buf, NULL, 10); }
        snprintf(bb, sz, "%s/../badblocks", dir);
    } else {
        snprintf(bb, sz, "%s/badblocks", dir);
    }
    return 0;
}

/* Рядок списку — «початок довжина» у 512-байтових секторах. */
static int in_badblocks(const char *path, unsigned long long sector,
                        unsigned long long *s0, unsigned long long *len)
{
    unsigned long long s, n;
    int hit = 0;
    FILE *f = fopen(path, "r");

    if (!f) return -1;
    while (fscanf(f, "%llu %llu", &s, &n) == 2)
        if (sector >= s && sector < s + n) { *s0 = s; *len = n; hit = 1; break; }
    fclose(f);
    return hit;
}
