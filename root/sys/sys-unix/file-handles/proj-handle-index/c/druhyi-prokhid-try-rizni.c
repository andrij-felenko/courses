struct rec {
    char uuid[64];
    int type;
    unsigned char h[MAX_HANDLE_SZ];
    unsigned hn;
    unsigned long long sum, size;
    char path[PATH_MAX];
};

static int read_rec(FILE *f, struct rec *r)
{
    char hex[2 * MAX_HANDLE_SZ + 1];
    size_t len;

    if (fscanf(f, "%63s %d %256s %16llx %llu %zu",
               r->uuid, &r->type, hex, &r->sum, &r->size, &len) != 6)
        return 0;
    if (fgetc(f) != ' ')                 /* рівно один пробіл, не «пропустити пробіли»: */
        return 0;                        /* ім'я файлу може починатися з пробілу */
    r->hn = 0;
    if (strcmp(hex, "-"))
        for (const char *p = hex; p[0] && p[1]; p += 2)
            sscanf(p, "%2hhx", &r->h[r->hn++]);
    if (len >= PATH_MAX || fread(r->path, 1, len, f) != len)
        return 0;
    r->path[len] = '\0';
    return fgetc(f) == '\n';
}

static int check(const char *idxpath)
{
    char line[256];
    struct rec r;
    FILE *f = fopen(idxpath, "r");

    if (!f) {
        perror(idxpath);
        return 1;
    }
    if (!fgets(line, sizeof line, f) || strncmp(line, "#handleidx 1", 12)) {
        fprintf(stderr, "%s: не той формат\n", idxpath);
        return 1;
    }
    if (!fgets(line, sizeof line, f))    /* рядок #fields */
        return 1;

    while (read_rec(f, &r)) {
        int mid, mfd, fd;

        if (!r.hn) {                     /* рукоятки немає — ФС її не вміє */
            printf("без ключа  %s\n", r.path);
            continue;
        }

        /* 1. Найдешевше: хто зараз лежить під збереженим іменем? */
        fh->handle_bytes = MAX_HANDLE_SZ;
        if (name_to_handle_at(AT_FDCWD, r.path, fh, &mid, 0) == 0 &&
            fh->handle_type == r.type && fh->handle_bytes == r.hn &&
            memcmp(fh->f_handle, r.h, r.hn) == 0) {
            printf("на місці   %s%s\n", r.path,
                   content_sum(r.path) == r.sum ? "" : "   (вміст змінився)");
            continue;
        }

        /* 2. Ім'я більше не веде до нашого файлу. Чи він узагалі живий? */
        if ((mfd = open_mount_by_uuid(r.uuid)) < 0) {
            printf("не видно   %s   (ФС %s не змонтована)\n", r.path, r.uuid);
            continue;
        }
        fh->handle_bytes = r.hn;
        fh->handle_type = r.type;
        memcpy(fh->f_handle, r.h, r.hn);

        fd = open_by_handle_at(mfd, fh, O_RDONLY);
        if (fd >= 0) {
            char link[64], now[PATH_MAX];
            ssize_t k;

            snprintf(link, sizeof link, "/proc/self/fd/%d", fd);
            k = readlink(link, now, sizeof now - 1);
            now[k > 0 ? k : 0] = '\0';
            printf("перейм.    %s → %s\n", r.path,
                   k > 0 ? now : "(шлях невідомий)");
            close(fd);
        } else if (errno == ESTALE) {
            printf("немає      %s\n", r.path);
        } else {
            perror("open_by_handle_at");  /* EPERM — бракує CAP_DAC_READ_SEARCH */
        }
        close(mfd);
    }
    fclose(f);
    return 0;
}

int main(int argc, char **argv)
{
    if (!(fh = malloc(sizeof *fh + MAX_HANDLE_SZ)))
        return 1;
    load_mounts();
    if (argc == 4 && !strcmp(argv[1], "scan"))
        return scan(argv[2], argv[3]);
    if (argc == 3 && !strcmp(argv[1], "check"))
        return check(argv[2]);
    fprintf(stderr, "вжиток: %s scan <корінь> <покажчик> | %s check <покажчик>\n",
            argv[0], argv[0]);
    return 2;
}
