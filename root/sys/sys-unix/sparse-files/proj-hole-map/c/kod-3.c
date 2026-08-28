int main(int argc, char **argv)
{
    enum { M_AUTO, M_ALWAYS, M_NEVER } mode = M_AUTO;
    int opt;

    while ((opt = getopt(argc, argv, "zn")) != -1) {
        switch (opt) {
        case 'z': mode = M_ALWAYS; break;
        case 'n': mode = M_NEVER;  break;
        default:  fprintf(stderr, "вжиток: %s [-z|-n] джерело копія\n", argv[0]);
                  return 2;
        }
    }
    if (argc - optind != 2) {
        fprintf(stderr, "вжиток: %s [-z|-n] джерело копія\n", argv[0]);
        return 2;
    }
    const char *src = argv[optind], *dst = argv[optind + 1];

    int sfd = open(src, O_RDONLY);
    if (sfd < 0) { perror(src); return 1; }

    struct stat ss;
    if (fstat(sfd, &ss) < 0) { perror("fstat джерела"); close(sfd); return 1; }
    if (!S_ISREG(ss.st_mode)) {
        fprintf(stderr, "%s: не звичайний файл — карти дір у нього немає\n", src);
        close(sfd); return 1;
    }

    /* Карта описує стан метаданих ЗАРАЗ. Скидаємо джерело на носій, щоб
       питати про рішення файлової системи, а не про її намір. */
    if (fsync(sfd) < 0)
        fprintf(stderr, "попередження: fsync джерела: %s\n", strerror(errno));

    /* O_EXCL, а не O_TRUNC: у наявному файлі під «дірою» лишився б його
       старий вміст — ми ж туди нічого не пишемо. Приймач мусить бути новим. */
    int dfd = open(dst, O_WRONLY | O_CREAT | O_EXCL, ss.st_mode & 07777);
    if (dfd < 0) { perror(dst); close(sfd); return 1; }

    struct stat ds;
    if (fstat(dfd, &ds) < 0) { perror("fstat копії"); close(sfd); close(dfd); return 1; }

    /* Вікно кратне блокові ПРИЙМАЧА: діру там можна лишити лише цілими блоками. */
    size_t unit = ds.st_blksize > 0 ? (size_t)ds.st_blksize : 4096u;
    size_t bufsz = unit < (1u << 20) ? (((1u << 20) + unit - 1) / unit) * unit : unit;
    char *buf = malloc(bufsz);
    if (!buf) { fprintf(stderr, "бракує пам'яті на %zu Б\n", bufsz);
                close(sfd); close(dfd); return 1; }

    off_t moved = 0, skipped = 0;
    long islands = 0;
    const char *how = NULL;
    int rc = 0;

    if (mode == M_AUTO) {
        int r = copy_by_map(sfd, dfd, ss.st_size, buf, bufsz, &moved, &islands);
        if (r == WALK_OK)         how = "карта SEEK_DATA/SEEK_HOLE";
        else if (r == WALK_ERROR) { perror("копіювання за картою"); rc = 1; }
        /* WALK_NO_MAP — мовчки на запасний шлях */
    }

    if (!rc && how == NULL) {
        int punch;
        if      (mode == M_ALWAYS) punch = 1;
        else if (mode == M_NEVER)  punch = 0;
        else /* карти немає — груба ознака: місця віддано менше, ніж обіцяно
                розміром. Одиниця st_blocks — 512 Б і з блоком ФС не пов'язана. */
            punch = (long long)ss.st_blocks * 512 < (long long)ss.st_size;

        if (copy_scanning(sfd, dfd, ss.st_size, buf, bufsz, punch, &moved, &skipped) < 0) {
            perror("копіювання"); rc = 1;
        } else {
            how = punch ? "пошук нульових вікон" : "суцільне копіювання";
        }
    }

    /* Розмір ставимо в кінці: якщо файл кінчається дірою, останній write
       стався раніше за кінець, і без цього копія вийшла б коротшою. */
    if (!rc && ftruncate(dfd, ss.st_size) < 0) { perror("ftruncate"); rc = 1; }
    /* Поки дані не осіли, st_blocks копії — ще не рішення, а намір. */
    if (!rc && fsync(dfd) < 0)                 { perror("fsync копії");  rc = 1; }

    struct stat fin;
    if (!rc && fstat(dfd, &fin) == 0) {
        long long src_used = (long long)ss.st_blocks  * 512;
        long long dst_used = (long long)fin.st_blocks * 512;
        printf("спосіб            %s\n", how);
        if (islands) printf("островів даних    %ld\n", islands);
        printf("перенесено        %lld Б\n", (long long)moved);
        if (skipped) printf("пропущено нулів   %lld Б\n", (long long)skipped);
        printf("джерело           st_size %lld, зайнято %lld Б\n",
               (long long)ss.st_size, src_used);
        printf("копія             st_size %lld, зайнято %lld Б\n",
               (long long)fin.st_size, dst_used);
        if (src_used < ss.st_size && dst_used >= ss.st_size)
            fprintf(stderr, "увага: у джерелі були діри, у копії їх немає — "
                            "приймач розрідженості не тримає\n");
    }

    free(buf);
    close(sfd);
    if (close(dfd) < 0 && !rc) { perror("close копії"); rc = 1; }
    return rc;
}
