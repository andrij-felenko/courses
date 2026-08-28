static int visit(const char *path, const struct stat *st, int flag, struct FTW *f)
{
    (void)path; (void)f;
    if (flag == FTW_NS)              /* stat не вдався — судити нема про що */
        return 0;

    struct rec *r = find(st->st_ino);
    r->seen++;                        /* нас відвідали під одним іменем */
    r->nlink = st->st_nlink;
    r->known = 1;
    return 0;
}

/* 64 — скільки каталогів дозволено тримати відкритими водночас */
nftw(root, visit, 64, FTW_PHYS | FTW_MOUNT);
