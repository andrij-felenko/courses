/* Пари (пристрій, inode) вже врахованих файлів. Порожня комірка — обидва нулі:
   inode з номером 0 не існує в жодній файловій системі. */
struct key { dev_t dev; ino_t ino; };
struct seen { struct key *v; size_t cap, n; };

static uint64_t mix(uint64_t x)
{
    x ^= x >> 33; x *= 0xff51afd7ed558ccdULL;
    x ^= x >> 33; x *= 0xc4ceb9fe1a85ec53ULL;
    return x ^ (x >> 33);
}

static int seen_grow(struct seen *s);

/* 1 — раніше не бачили (рахувати), 0 — уже врахований, −1 — брак пам'яті. */
static int seen_add(struct seen *s, dev_t dev, ino_t ino)
{
    if (s->n * 2 >= s->cap && seen_grow(s) < 0)
        return -1;

    size_t mask = s->cap - 1;
    size_t i = (size_t)(mix((uint64_t)dev * 1000003u ^ (uint64_t)ino) & mask);
    while (s->v[i].ino || s->v[i].dev) {
        if (s->v[i].dev == dev && s->v[i].ino == ino)
            return 0;
        i = (i + 1) & mask;
    }
    s->v[i].dev = dev;
    s->v[i].ino = ino;
    s->n++;
    return 1;
}

static int seen_grow(struct seen *s)
{
    size_t cap = s->cap ? s->cap * 2 : 1024;
    struct seen t = { calloc(cap, sizeof(struct key)), cap, 0 };
    if (!t.v)
        return -1;
    for (size_t i = 0; i < s->cap; i++)          /* перерозкладаємо старі ключі */
        if (s->v[i].ino || s->v[i].dev)
            seen_add(&t, s->v[i].dev, s->v[i].ino);
    free(s->v);
    *s = t;
    return 0;
}

struct ctx {
    struct seen seen;
    dev_t root_dev;               /* межа: за точку монтування не виходимо */
    int max_depth;
    unsigned long long bytes;
    unsigned long long errors;
};

static void walk(struct ctx *c, int dfd, const char *label, int depth)
{
    DIR *dp = fdopendir(dfd);
    if (!dp) {
        fprintf(stderr, "fdopendir %s: %s\n", label, strerror(errno));
        close(dfd);               /* невдалий fdopendir дескриптор не забирає */
        c->errors++;
        return;
    }
    int d = dirfd(dp);            /* той самий дескриптор, здобутий законним шляхом */

    struct dirent *e;
    while (errno = 0, (e = readdir(dp)) != NULL) {
        char name[NAME_MAX + 1];
        size_t len = strnlen(e->d_name, sizeof name);
        if (len >= sizeof name) { c->errors++; continue; }
        memcpy(name, e->d_name, len + 1);   /* буфер потоку більше не чіпаємо */

        if (name[0] == '.' &&
            (name[1] == '\0' || (name[1] == '.' && name[2] == '\0')))
            continue;                        /* «.» і «..» — не наші */

        struct stat st;
        if (fstatat(d, name, &st, AT_SYMLINK_NOFOLLOW) < 0) {
            fprintf(stderr, "stat %s/%s: %s\n", label, name, strerror(errno));
            c->errors++;
            continue;
        }

        /* Каталоги пропускаємо: у них nlink ≥ 2 через «.», і в дереві
           кожен трапляється рівно раз. Решту з кількома іменами — рахуємо раз. */
        if (!S_ISDIR(st.st_mode) && st.st_nlink > 1) {
            int fresh = seen_add(&c->seen, st.st_dev, st.st_ino);
            if (fresh < 0) {                 /* брак пам'яті — далі не йдемо */
                fprintf(stderr, "seen: не вистачило пам'яті\n");
                c->errors++;
                errno = 0;                   /* щоб не сплутати з помилкою readdir */
                break;
            }
            if (fresh == 0) continue;
        }

        c->bytes += (unsigned long long)st.st_blocks * 512;

        if (!S_ISDIR(st.st_mode))
            continue;
        if (st.st_dev != c->root_dev)
            continue;                        /* інша файлова система */
        if (depth + 1 >= c->max_depth) {
            fprintf(stderr, "надто глибоко: %s/%s\n", label, name);
            c->errors++;
            continue;
        }

        int sub = openat(d, name, O_RDONLY | O_DIRECTORY | O_NOFOLLOW | O_CLOEXEC);
        if (sub < 0) {
            fprintf(stderr, "openat %s/%s: %s\n", label, name, strerror(errno));
            c->errors++;
            continue;
        }
        walk(c, sub, name, depth + 1);       /* власність на sub переходить туди */
    }
    if (errno != 0) {
        fprintf(stderr, "readdir %s: %s\n", label, strerror(errno));
        c->errors++;
    }

    closedir(dp);                            /* закриває d */
}

int main(int argc, char **argv)
{
    const char *root = (argc > 1) ? argv[1] : ".";

    /* Кожен рівень рекурсії тримає відкритим один каталог, тож глибину
       обмежуємо половиною бюджету дескрипторів процесу. */
    struct rlimit rl;
    int max_depth = 256;
    if (getrlimit(RLIMIT_NOFILE, &rl) == 0 && rl.rlim_cur != RLIM_INFINITY) {
        int half = (int)(rl.rlim_cur / 2);
        if (half < max_depth)
            max_depth = half;
    }
    if (max_depth < 8) {
        fprintf(stderr, "замало дескрипторів для обходу\n");
        return 1;
    }

    /* Корінь обходу назвав користувач — тут посилання дозволене свідомо;
       усе, що глибше, відкриватимемо вже з O_NOFOLLOW. */
    int rfd = open(root, O_RDONLY | O_DIRECTORY | O_CLOEXEC);
    if (rfd < 0) { perror(root); return 1; }

    struct stat st;
    if (fstat(rfd, &st) < 0) { perror("fstat"); close(rfd); return 1; }

    struct ctx c = {0};
    c.root_dev  = st.st_dev;
    c.max_depth = max_depth;
    c.bytes     = (unsigned long long)st.st_blocks * 512;   /* сам кореневий каталог */

    walk(&c, rfd, root, 0);

    printf("%llu байтів (%llu КіБ)\n", c.bytes, c.bytes / 1024);
    if (c.errors)
        fprintf(stderr, "пропущено через помилки: %llu\n", c.errors);
    free(c.seen.v);
    return c.errors ? 2 : 0;
}
