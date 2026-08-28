/* одне рішення: надрукувати клас, потрібні букви й вердикт для об'єкта за fd */
static int step(const char *mark, const char *name, int fd,
                const struct ident *me, unsigned want)
{
    struct stat st;
    enum cls c;
    const char *rule;
    int ok;

    if (fstat(fd, &st) < 0) { perror("fstat"); return -1; }
    ok = decide(&st, me, want, &c, &rule);
    printf("  %s %-14s %04o  потрібно %c%c%c → %s  [клас %s; %s]\n",
           mark, name, (unsigned)(st.st_mode & 07777),
           want & WANT_R ? 'r' : '-', want & WANT_W ? 'w' : '-',
           want & WANT_X ? 'x' : '-', ok ? "так" : "НІ", cls_name[c], rule);
    return ok;
}

static int walk(const char *path, const struct ident *me, unsigned want)
{
    char buf[PATH_MAX], *comp, *next, *save = NULL;
    const char *here = path[0] == '/' ? "/" : ".";
    int dirfd, ok, verdict = 1;

    if (strlen(path) >= sizeof buf) { fprintf(stderr, "задовгий шлях\n"); return -1; }
    strcpy(buf, path);

    dirfd = open(here, O_PATH | O_DIRECTORY);
    if (dirfd < 0) { perror(here); return -1; }

    comp = strtok_r(buf, "/", &save);
    if (!comp) {                        /* «/» або «.» — ціль і є цей каталог */
        ok = step("└", here, dirfd, me, want);
        close(dirfd);
        return ok;
    }

    for (; comp; comp = next) {
        int fd;
        next = strtok_r(NULL, "/", &save);

        ok = step("├", here, dirfd, me, WANT_X);   /* пошук імені в цьому каталозі */
        if (ok < 0) { close(dirfd); return -1; }
        verdict &= ok;

        fd = openat(dirfd, comp, O_PATH);   /* без O_NOFOLLOW: посилання йдуть як у ядрі */
        close(dirfd);
        if (fd < 0) {
            printf("  openat(\"%s\") → %s%s\n", comp, strerror(errno),
                   errno == EACCES && ok ? "   ← наш вердикт розійшовся з ядровим" : "");
            return -1;
        }
        dirfd = fd;
        here = comp;
    }

    ok = step("└", here, dirfd, me, want);          /* дійшли: dirfd — це вже ціль */
    close(dirfd);
    return ok < 0 ? -1 : (verdict & ok);
}

int main(int argc, char **argv)
{
    struct ident me;
    unsigned want = 0;
    int amode = 0, mine, fd;

    if (argc != 3) {
        fprintf(stderr, "вжиток: %s rwx ШЛЯХ\n", argv[0]);
        return 2;
    }
    for (const char *p = argv[1]; *p; p++)
        switch (*p) {
        case 'r': want |= WANT_R; amode |= R_OK; break;
        case 'w': want |= WANT_W; amode |= W_OK; break;
        case 'x': want |= WANT_X; amode |= X_OK; break;
        default: fprintf(stderr, "невідома буква: %c\n", *p); return 2;
        }

    who_am_i(&me);
    printf("я: fsuid=%u fsgid=%u груп=%d CapEff=%016llx\n",
           (unsigned)me.fsuid, (unsigned)me.fsgid, me.ngroups, me.capeff);

    mine = walk(argv[2], &me, want);
    printf("\nмій вердикт          : %s\n",
           mine < 0 ? "обхід урвався" : mine ? "дозволено" : "заборонено");

    errno = 0;
    printf("access()             : %s   (реальні UID/GID)\n",
           access(argv[2], amode) == 0 ? "дозволено" : strerror(errno));
    errno = 0;
    printf("faccessat AT_EACCESS : %s   (дійсні)\n",
           faccessat(AT_FDCWD, argv[2], amode, AT_EACCESS) == 0
               ? "дозволено" : strerror(errno));

    if (want == WANT_R) {
        errno = 0;
        fd = open(argv[2], O_RDONLY);
        printf("справжній open()     : %s\n", fd >= 0 ? "дозволено" : strerror(errno));
        if (fd >= 0)
            close(fd);
    }
    free(me.groups);
    return 0;
}
