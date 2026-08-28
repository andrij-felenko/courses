static int visit(const char *path, const struct stat *st, int type, struct FTW *ft)
{
    (void)ft;
    if (type != FTW_F || !S_ISREG(st->st_mode)) return 0;
    if (st->st_dev != root_dev)                 return 0;  /* була б EXDEV     */
    if ((uint64_t)st->st_size < win)            return 0;  /* нема жодного вікна */

    fr = grow(fr, &cfr, nfr + 1, sizeof *fr);
    struct filerec *f = &fr[nfr++];
    memset(f, 0, sizeof *f);
    f->path = strdup(path);
    f->ino  = st->st_ino;
    f->nwin = (uint32_t)((uint64_t)st->st_size / win);   /* хвіст нижче вікна відкидаємо */
    if (!f->path) { fprintf(stderr, "бракує пам'яті\n"); exit(1); }
    return 0;
}

static int inocmp(const void *A, const void *B)
{
    ino_t a = ((const struct filerec *)A)->ino, b = ((const struct filerec *)B)->ino;
    return a < b ? -1 : (a > b);
}

static void drop_hardlinks(void)
{
    if (nfr < 2) return;
    qsort(fr, nfr, sizeof *fr, inocmp);
    size_t k = 1;
    for (size_t i = 1; i < nfr; i++) {
        if (fr[i].ino == fr[k - 1].ino) { free(fr[i].path); continue; }
        fr[k++] = fr[i];
    }
    nfr = k;
}
