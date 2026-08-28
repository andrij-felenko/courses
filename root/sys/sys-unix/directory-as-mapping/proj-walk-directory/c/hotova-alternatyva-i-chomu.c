static unsigned long long total;

static int visit(const char *path, const struct stat *st, int type, struct FTW *f)
{
    (void)path; (void)f;
    if (type == FTW_NS)                       /* stat не вдався */
        return 0;
    total += (unsigned long long)st->st_blocks * 512;
    return 0;
}

/* 64 — скільки каталогів дозволено тримати відкритими водночас */
nftw(root, visit, 64, FTW_PHYS | FTW_MOUNT);
